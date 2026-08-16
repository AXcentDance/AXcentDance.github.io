#!/usr/bin/env python3
"""Critical-CSS pipeline: inline above-the-fold CSS, async-load the full sheets.

Every page carries:
  <style data-critical="HASH">...</style>            (above-fold rules, minified)
  <link rel="stylesheet" href="style.min.css?v=X" media="print"
        onload="this.media='all'" data-async-css>    (full sheet, non-blocking)
  <noscript><link rel="stylesheet" href="style.min.css?v=X"></noscript>

Blog pages get the same treatment for blog-post.min.css (rules merged into the
one critical block). The CSP on every page allows both the inline style block
and the inline onload handler (style-src/script-src 'unsafe-inline').

Modes:
  export   write System/flatten/critical_rules.json for the browser harness
           (System/flatten/critical.html), which produces critical_ids.json.
  apply    assemble per-page critical blocks from critical_ids.json and inject
           into every page in pages.json.
  --check  freshness gate (run by site_health): every page must carry a
           critical block whose hash matches sha1(css sources + page body).

Regenerate whenever style.css / blog-post.css change or a page's above-fold
markup changes: export -> harness -> apply. The hash covers CSS bytes and the
page body, so staleness fails the gate instead of shipping silently.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLAT = ROOT / 'System' / 'flatten'
sys.path.insert(0, str(FLAT))
from analyze_rules import parse_css, test_selector  # noqa: E402

ESBUILD = 'esbuild@0.24.0'
SOURCES = ['style.css', 'blog-post.css']
# Widths the harness samples. A @media band that excludes BOTH of them would
# otherwise be invisible to extraction — but the inline block is served to
# EVERY device, so those rules must still be included (they stay wrapped in
# their @media, so they only apply on the devices they were written for).
SAMPLE_WIDTHS = (375, 1280)
LINK_RE = re.compile(
    r'<link rel="stylesheet" href="(?P<prefix>[./]*)'
    r'(?P<file>style|blog-post)\.min\.css\?v=(?P<v>[0-9.]+)"'
    r'(?P<attrs>[^>]*)>')
CRITICAL_RE = re.compile(
    r'<style data-critical="(?P<hash>[0-9a-f]{16})">.*?</style>\n?', re.S)
NOSCRIPT_RE = re.compile(
    r'<noscript><link rel="stylesheet" href="[^"]*"></noscript>\n?')
REL_URL = re.compile(r"url\(\s*(['\"]?)(?!/|data:|https?:|#)([^)'\"]+)\1\s*\)")


def source_rules():
    """Parse both sheets into one ordered unit list with global ids."""
    all_units = []
    for name in SOURCES:
        text = (ROOT / name).read_text(encoding='utf-8')
        for u in parse_css(text):
            u['sheet'] = name
            all_units.append(u)
    for i, u in enumerate(all_units):
        u['id'] = i
    return all_units


def width_gap(query):
    """True when a @media query's width conditions exclude every sample width."""
    mins = [int(x) for x in re.findall(r'min-width:\s*(\d+)px', query)]
    maxs = [int(x) for x in re.findall(r'max-width:\s*(\d+)px', query)]
    if not mins and not maxs:
        return False
    return not any(all(w >= v for v in mins) and all(w <= v for v in maxs)
                   for w in SAMPLE_WIDTHS)


def cmd_export():
    units = source_rules()
    out = []
    for u in units:
        if u['kind'] != 'rule':
            continue
        gap = any(c.lstrip('@').startswith('media') and width_gap(c)
                  for c in u['context'])
        tests = []
        always = False
        for sel in u['selectors']:
            t = test_selector(sel)
            if t is None:
                always = True
            else:
                tests.append(t)
        out.append({'id': u['id'], 'sheet': u['sheet'],
                    'context': u['context'], 'gap': gap,
                    'tests': tests, 'always': always})
    (FLAT / 'critical_rules.json').write_text(json.dumps(out))
    n_always = sum(1 for r in out if r['always'])
    n_gap = sum(1 for r in out if r['gap'])
    print(f'{len(out)} rules exported ({n_always} always-include, '
          f'{n_gap} in unsampled viewport bands); '
          f'open /System/flatten/critical.html and run `await runCritical()`')


def minify_block(css):
    r = subprocess.run(['npx', '-y', ESBUILD, '--loader=css', '--minify'],
                       input=css.encode('utf-8'), capture_output=True,
                       cwd=ROOT, timeout=120)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode('utf-8', 'replace'))
        raise SystemExit('esbuild failed on a critical block')
    return r.stdout.decode('utf-8').strip()


def page_hash(page_text, uses_blog, css_texts):
    body = page_text.split('<body', 1)[1] if '<body' in page_text else page_text
    h = hashlib.sha1()
    h.update(css_texts['style.css'].encode('utf-8'))
    if uses_blog:
        h.update(css_texts['blog-post.css'].encode('utf-8'))
    h.update(body.encode('utf-8'))
    return h.hexdigest()[:16]


def assemble(units, ids):
    """Emit included units in source order, restoring @-context wrappers."""
    incl = set(ids)
    by_id = {u['id']: u for u in units}

    # always include :root / @font-face; keyframes by reference below
    for u in units:
        if u['kind'] == 'fontface':
            incl.add(u['id'])
        if u['kind'] == 'rule' and any(
                s.strip() in (':root', 'html', 'body', '*')
                for s in u['selectors']):
            incl.add(u['id'])

    body_blob = ' '.join(
        by_id[i]['body'] for i in incl if by_id[i]['kind'] == 'rule')
    for u in units:
        if u['kind'] == 'keyframes':
            name = u['name']
            if re.search(r'animation[^;}]*[\s:,]' + re.escape(name) + r'\b',
                         body_blob):
                incl.add(u['id'])

    texts = {name: (ROOT / name).read_text(encoding='utf-8')
             for name in SOURCES}
    parts = []
    open_ctx = []
    for u in units:
        if u['id'] not in incl or u['kind'] in ('at-open', 'at-close',
                                                'at-simple', 'at-other'):
            continue
        ctx = u['context']
        while open_ctx and open_ctx != ctx[:len(open_ctx)]:
            parts.append('}')
            open_ctx = open_ctx[:-1]
        for c in ctx[len(open_ctx):]:
            parts.append(c + '{')
            open_ctx = open_ctx + [c]
        parts.append(texts[u['sheet']][u['start']:u['end']])
    while open_ctx:
        parts.append('}')
        open_ctx = open_ctx[:-1]
    css = '\n'.join(parts)
    # inline blocks resolve url() against the PAGE, so root-relative only
    css = REL_URL.sub(lambda m: 'url(/' + m.group(2) + ')', css)
    return css


def async_links(prefix, style_v, blog_v):
    lines = [
        f'<link rel="stylesheet" href="{prefix}style.min.css?v={style_v}" '
        f'media="print" onload="this.media=\'all\'" data-async-css>',
        f'<noscript><link rel="stylesheet" '
        f'href="{prefix}style.min.css?v={style_v}"></noscript>']
    if blog_v:
        lines += [
            f'<link rel="stylesheet" href="{prefix}blog-post.min.css?v={blog_v}" '
            f'media="print" onload="this.media=\'all\'" data-async-css>',
            f'<noscript><link rel="stylesheet" '
            f'href="{prefix}blog-post.min.css?v={blog_v}"></noscript>']
    return lines


def cmd_apply():
    units = source_rules()
    ids_by_page = json.loads((FLAT / 'critical_ids.json').read_text())
    css_texts = {name: (ROOT / name).read_text(encoding='utf-8')
                 for name in SOURCES}
    cache = {}
    n = 0
    for page, ids in sorted(ids_by_page.items()):
        p = ROOT / page.lstrip('/')
        text = p.read_text(encoding='utf-8')
        # normalize back to plain blocking links (idempotent re-apply)
        text = CRITICAL_RE.sub('', text)
        text = NOSCRIPT_RE.sub('', text)
        links = list(LINK_RE.finditer(text))
        if not links:
            print(f'SKIP {page}: no stylesheet link found')
            continue
        style_link = next(m for m in links if m.group('file') == 'style')
        blog_link = next((m for m in links if m.group('file') == 'blog-post'),
                         None)
        key = tuple(sorted(ids))
        if key not in cache:
            cache[key] = minify_block(assemble(units, ids))
        h = page_hash(text, bool(blog_link), css_texts)
        block = (f'<style data-critical="{h}">{cache[key]}</style>\n    '
                 + '\n    '.join(async_links(style_link.group('prefix'),
                                             style_link.group('v'),
                                             blog_link and blog_link.group('v'))))
        # replace the style link with the block; drop the blog link line
        if blog_link:
            text = re.sub(re.escape(blog_link.group(0)) + r'\n?', '', text)
        text = LINK_RE.sub(lambda m: block if m.group('file') == 'style'
                           else m.group(0), text, count=len(links))
        p.write_text(text, encoding='utf-8')
        n += 1
    sizes = sorted(len(v) for v in cache.values())
    print(f'{n} pages injected; {len(cache)} unique blocks, '
          f'min {sizes[0]}B max {sizes[-1]}B median {sizes[len(sizes)//2]}B')


def cmd_check():
    css_texts = {name: (ROOT / name).read_text(encoding='utf-8')
                 for name in SOURCES}
    pages = json.loads((FLAT / 'pages.json').read_text())
    bad = []
    for page in pages:
        p = ROOT / page.lstrip('/')
        text = p.read_text(encoding='utf-8')
        m = CRITICAL_RE.search(text)
        if not m:
            bad.append(f'{page}: no critical block')
            continue
        if 'data-async-css' not in text or '<noscript><link' not in text:
            bad.append(f'{page}: async/noscript pattern missing')
            continue
        uses_blog = 'blog-post.min.css' in text
        clean = CRITICAL_RE.sub('', text)
        if page_hash(clean, uses_blog, css_texts) != m.group('hash'):
            bad.append(f'{page}: critical block STALE '
                       '(CSS or body changed since generation)')
    if bad:
        print('\n'.join(bad))
        print(f'FAIL: {len(bad)} page(s) with stale/missing critical CSS. '
              'Re-run: critical_css.py export -> critical.html harness -> apply')
        sys.exit(1)
    print(f'PASS: critical CSS fresh on {len(pages)} pages.')


if __name__ == '__main__':
    {'export': cmd_export, 'apply': cmd_apply,
     '--check': cmd_check}[sys.argv[1]]()
