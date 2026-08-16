#!/usr/bin/env python3
"""Byte-faithful style.css rule inventory + site-wide-unused rule purge.

Workflow (see README.md):
  1. python3 analyze_rules.py parse
       -> writes rules.json, selectors.json, pages.json next to this script.
  2. Serve the repo, open /System/flatten/usage.html, run `await runUsage()`,
     save the returned unmatched-selector list to unmatched.json here.
  3. python3 analyze_rules.py kill
       -> applies the JS poison guard, deletes rules whose EVERY selector is
          unmatched and unpoisoned, prunes empty @media shells and orphaned
          @keyframes, rewrites ../../style.css. Verify with fingerprint.html.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CSS = ROOT / 'style.css'

# Pseudo-classes that only reflect runtime state: strip for static testing.
STATE_PSEUDO = re.compile(
    r':(hover|focus-visible|focus-within|focus|active|visited|link|target|'
    r'checked|disabled|enabled|valid|invalid|required|optional|'
    r'placeholder-shown|fullscreen|modal|popover-open)\b')
PSEUDO_ELEMENT = re.compile(r'::-?[a-zA-Z][a-zA-Z-]*(\(\))?'
                            r'|:(before|after|first-line|first-letter)\b')


def parse_css(text):
    """Split CSS into units with absolute byte spans.

    Returns list of dicts:
      {kind: 'rule'|'at-block'|'at-simple'|'keyframes'|'fontface',
       start, end, selectors (rules), context (list of @-prelude strings),
       name (keyframes), body (rule body text)}
    """
    units = []
    n = len(text)
    i = 0

    def skip_ws_comments(j):
        while j < n:
            if text[j].isspace():
                j += 1
            elif text.startswith('/*', j):
                k = text.find('*/', j + 2)
                j = n if k < 0 else k + 2
            else:
                break
        return j

    def find_block_end(j):
        """j points at '{'. Return index just past the matching '}'."""
        depth = 0
        while j < n:
            c = text[j]
            if text.startswith('/*', j):
                k = text.find('*/', j + 2)
                j = n if k < 0 else k + 2
                continue
            if c in '"\'':
                q = c
                j += 1
                while j < n and text[j] != q:
                    j += 2 if text[j] == '\\' else 1
                j += 1
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return j + 1
            j += 1
        return n

    def walk(j, end, context):
        while True:
            j = skip_ws_comments(j)
            if j >= end:
                return
            start = j
            # find prelude end: '{' or ';'
            k = j
            brace = -1
            while k < end:
                c = text[k]
                if text.startswith('/*', k):
                    m = text.find('*/', k + 2)
                    k = end if m < 0 else m + 2
                    continue
                if c in '"\'':
                    q = c
                    k += 1
                    while k < end and text[k] != q:
                        k += 2 if text[k] == '\\' else 1
                    k += 1
                    continue
                if c == '{':
                    brace = k
                    break
                if c == ';':
                    break
                k += 1
            if brace < 0:
                # simple statement (@import/@charset) or trailing junk
                stop = min(k + 1, end)
                units.append({'kind': 'at-simple', 'start': start, 'end': stop,
                              'context': context, 'prelude': text[start:k].strip()})
                j = stop
                continue
            prelude = re.sub(r'/\*.*?\*/', ' ', text[start:brace], flags=re.S).strip()
            block_end = find_block_end(brace)
            if prelude.startswith('@'):
                low = prelude.lower()
                if low.startswith(('@media', '@supports', '@layer', '@container')):
                    units.append({'kind': 'at-open', 'start': start,
                                  'body_start': brace + 1, 'end': block_end,
                                  'context': context, 'prelude': prelude})
                    walk(brace + 1, block_end - 1, context + [prelude])
                    units.append({'kind': 'at-close', 'start': block_end,
                                  'end': block_end, 'context': context,
                                  'prelude': prelude})
                elif low.startswith('@keyframes') or low.startswith('@-webkit-keyframes'):
                    name = prelude.split()[-1]
                    units.append({'kind': 'keyframes', 'start': start,
                                  'end': block_end, 'context': context,
                                  'name': name})
                elif low.startswith('@font-face'):
                    units.append({'kind': 'fontface', 'start': start,
                                  'end': block_end, 'context': context})
                else:
                    units.append({'kind': 'at-other', 'start': start,
                                  'end': block_end, 'context': context,
                                  'prelude': prelude})
            else:
                sels = split_selectors(prelude)
                units.append({'kind': 'rule', 'start': start, 'end': block_end,
                              'context': context, 'selectors': sels,
                              'body': text[brace + 1:block_end - 1]})
            j = block_end

    walk(0, n, [])
    return units


def split_selectors(prelude):
    """Split a selector list on top-level commas."""
    out, depth, cur = [], 0, []
    for ch in prelude:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append(''.join(cur).strip())
    return [s for s in out if s]


def test_selector(sel):
    """The statically-testable form of a selector, or None if always-keep."""
    s = PSEUDO_ELEMENT.sub('', sel)
    s = STATE_PSEUDO.sub('', s).strip()
    s = re.sub(r'\s+', ' ', s)
    # a state-pseudo on its own compound leaves a dangling combinator part
    s = re.sub(r'(^| )([>+~]) ', r'\1\2 ', s).strip()
    if not s or s in ('*', 'html', 'body', ':root') or s.startswith(':root'):
        return None
    if s.startswith(('>', '+', '~')) or s.endswith(('>', '+', '~')):
        return None
    return s


def cmd_parse():
    text = CSS.read_text(encoding='utf-8')
    units = parse_css(text)
    rules = [u for u in units if u['kind'] == 'rule']
    sel_map = {}
    for idx, u in enumerate(units):
        if u['kind'] != 'rule':
            continue
        for sel in u['selectors']:
            t = test_selector(sel)
            if t is not None:
                sel_map.setdefault(t, [])
    (HERE / 'rules.json').write_text(json.dumps(units))
    (HERE / 'selectors.json').write_text(json.dumps(sorted(sel_map)))
    pages = sorted(
        str(p.relative_to(ROOT)) for p in ROOT.rglob('*.html')
        if 'node_modules' not in p.parts and 'System' not in p.parts
        and 'style.min.css' in p.read_text(encoding='utf-8'))
    (HERE / 'pages.json').write_text(json.dumps(['/' + p for p in pages]))
    total = sum(u['end'] - u['start'] for u in units if u['kind'] == 'rule')
    print(f'{len(units)} units, {len(rules)} style rules, '
          f'{len(sel_map)} testable selectors, {len(pages)} pages, '
          f'{total} rule bytes')


def js_poison_tokens():
    """Word tokens from every script that can touch the DOM at runtime."""
    token_re = re.compile(r'[A-Za-z_][A-Za-z0-9_-]{2,}')
    tokens = set()
    for name in ('script.js', 'script-blog.min.js', 'hls-video.js',
                 'meta-pixel.js'):
        p = ROOT / name
        if p.exists():
            tokens.update(token_re.findall(p.read_text(encoding='utf-8')))
    inline_re = re.compile(r'<script(?![^>]*type="application/ld\+json")'
                           r'[^>]*>(.*?)</script>', re.S | re.I)
    for page in json.loads((HERE / 'pages.json').read_text()):
        text = (ROOT / page.lstrip('/')).read_text(encoding='utf-8')
        for body in inline_re.findall(text):
            tokens.update(token_re.findall(body))
    return tokens


NAME_RE = re.compile(r'[.#]([A-Za-z_-][A-Za-z0-9_-]*)|\[\s*([A-Za-z-]+)')


def declared_names():
    """Every class/id/attr name declared anywhere: static HTML or any script.

    A selector containing a name that appears in NEITHER can never match,
    not even after JS mutations — nothing in the codebase produces the name.
    """
    names = set(js_poison_tokens())
    attr_re = re.compile(r'(?:^|[\s"\'])([a-zA-Z][a-zA-Z-]*)=')
    class_re = re.compile(r'(?:class|id)\s*=\s*"([^"]*)"')
    for page in json.loads((HERE / 'pages.json').read_text()):
        text = (ROOT / page.lstrip('/')).read_text(encoding='utf-8')
        for m in class_re.finditer(text):
            names.update(m.group(1).split())
        names.update(attr_re.findall(text))
    return names


def provably_dead(sel, declared):
    for m in NAME_RE.finditer(sel):
        name = m.group(1) or m.group(2)
        if name not in declared:
            return True
    return False


def cmd_kill():
    text = CSS.read_text(encoding='utf-8')
    units = json.loads((HERE / 'rules.json').read_text())
    unmatched = set(json.loads((HERE / 'unmatched.json').read_text()))
    declared = declared_names()

    kills, kept_conservative = [], 0
    for u in units:
        if u['kind'] != 'rule':
            continue
        verdicts = []
        for sel in u['selectors']:
            t = test_selector(sel)
            if t is None or t not in unmatched:
                verdicts.append('used')
            elif provably_dead(sel, declared):
                verdicts.append('dead')
            else:
                verdicts.append('kept')
        if verdicts and all(v == 'dead' for v in verdicts):
            kills.append(u)
        elif 'kept' in verdicts and 'used' not in verdicts:
            kept_conservative += 1

    # orphaned keyframes: names unreferenced once killed rules are gone
    kill_spans = [(u['start'], u['end']) for u in kills]

    def survives(unit):
        return not any(s <= unit['start'] and unit['end'] <= e
                       for s, e in kill_spans)

    anim_text = []
    for u in units:
        if u['kind'] == 'rule' and survives(u):
            anim_text.append(u['body'])
    anim_blob = ' '.join(anim_text)
    for u in units:
        if u['kind'] == 'keyframes':
            name = u['name']
            if not re.search(r'(animation[^;]*[\s:,]' + re.escape(name)
                             + r'\b)', anim_blob):
                kills.append(u)

    kills.sort(key=lambda u: u['start'])
    out, pos, removed = [], 0, 0
    for u in kills:
        out.append(text[pos:u['start']])
        pos = u['end']
        removed += u['end'] - u['start']
    out.append(text[pos:])
    new = ''.join(out)
    # prune @media/@supports shells left empty (repeat for nesting)
    shell = re.compile(r'@(media|supports)[^{};]*\{\s*\}')
    while True:
        new2 = shell.sub('', new)
        if new2 == new:
            break
        new = new2
    CSS.write_text(new, encoding='utf-8')
    n_rules = sum(1 for u in kills if u['kind'] == 'rule')
    n_kf = sum(1 for u in kills if u['kind'] == 'keyframes')
    print(f'killed {n_rules} rules + {n_kf} keyframes, {removed} bytes; '
          f'{kept_conservative} unmatched rules kept (runtime-state names); '
          f'{len(text)} -> {len(new)} bytes')
    (HERE / 'killed.json').write_text(json.dumps(
        [{'start': u['start'], 'end': u['end'],
          'what': u.get('selectors') or u.get('name')} for u in kills], indent=1))


if __name__ == '__main__':
    {'parse': cmd_parse, 'kill': cmd_kill}[sys.argv[1]]()
