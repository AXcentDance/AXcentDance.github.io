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
  export   diff the current CSS against System/flatten/critical_map.json and
           write critical_rules.json + probe_pages.json (ONLY the pages whose
           above-fold rule sets could actually have changed) for the browser
           harness (System/flatten/critical.html).
  apply    ingest the harness output (critical_ids.json), update the map, and
           assemble/inject per-page critical blocks into every page.
  --check  freshness gate (run by site_health): every page must carry a
           critical block whose hash matches sha1(css sources + page body).

INCREMENTAL MODEL (2026-08-16). Rules are tracked by a content key =
sha1(@-contexts + selector list) — declarations are excluded, because whether
a rule matches above the fold depends only on its selectors and media context.
critical_map.json stores, per page, the KEYS that matched, plus the universe
of keys ever accounted for. Consequences:

  - Editing declarations inside existing rules: no key changes, no probing.
    `export` reports zero pages; run `apply` directly (seconds).
  - Deleting rules: keys drop out of assembly automatically. No probing.
  - Adding/renaming a rule or its @media context: a NEW key appears. Its
    candidate pages are computed statically — a selector can only match a
    page whose HTML (or the site's first-party JS, for script-added classes)
    contains every class/id token outside :not()/:is() arguments — and only
    those pages are listed in probe_pages.json for the harness. A selector
    with no class/id tokens (e.g. `h2`, `[hidden]`) is unfilterable and
    probes everywhere; a rule with an always-include selector (`body`,
    `:root`, `*`) is added to every page without probing, mirroring the
    harness's own `always` handling.

The map is never pruned: keys of deleted rules keep their last-known match
results, so reverting a deletion costs nothing. Markup-only edits follow the
established convention: re-run `apply` (hashes cover page bodies); re-probe
via export/harness only when an ABOVE-FOLD markup change could alter which
rules match.
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
MAP_FILE = FLAT / 'critical_map.json'
RULES_FILE = FLAT / 'critical_rules.json'
IDS_FILE = FLAT / 'critical_ids.json'
PROBE_FILE = FLAT / 'probe_pages.json'
# Widths the harness samples. A @media band that excludes BOTH of them would
# otherwise be invisible to extraction — but the inline block is served to
# EVERY device, so those rules must still be included (they stay wrapped in
# their @media, so they only apply on the devices they were written for).
SAMPLE_WIDTHS = (375, 1280)
LINK_RE = re.compile(
    r'<link rel="stylesheet" href="(?P<prefix>[./]*)'
    r'(?P<file>style|blog-post)\.min\.css\?v=(?P<v>[0-9.]+)"'
    r'(?P<attrs>[^>]*)>')
# leading [ \t]* keeps apply byte-idempotent: without it every strip/reinject
# cycle left the removed line's indentation behind (4 spaces of drift per run)
CRITICAL_RE = re.compile(
    r'[ \t]*<style data-critical="(?P<hash>[0-9a-f]{16})">.*?</style>\n?', re.S)
NOSCRIPT_RE = re.compile(
    r'[ \t]*<noscript><link rel="stylesheet" href="[^"]*"></noscript>\n?')
REL_URL = re.compile(r"url\(\s*(['\"]?)(?!/|data:|https?:|#)([^)'\"]+)\1\s*\)")
PSEUDO_FN = re.compile(r':[a-zA-Z-]+\([^()]*\)')
CLASS_ID_TOKEN = re.compile(r'[.#]([A-Za-z0-9_-]+)')


def source_rules():
    """Parse both sheets into one ordered unit list with global ids + keys."""
    all_units = []
    for name in SOURCES:
        text = (ROOT / name).read_text(encoding='utf-8')
        for u in parse_css(text):
            u['sheet'] = name
            all_units.append(u)
    for i, u in enumerate(all_units):
        u['id'] = i
        if u['kind'] == 'rule':
            u['key'] = rule_key(u)
    return all_units


def rule_key(u):
    """Stable content key: selectors + @-contexts, declarations excluded.
    Match results depend only on these, so declaration edits keep the key."""
    ctx = '|'.join(re.sub(r'\s+', ' ', c).strip() for c in u['context'])
    sels = '|'.join(re.sub(r'\s+', ' ', s).strip() for s in u['selectors'])
    return hashlib.sha1(f'{ctx}||{sels}'.encode('utf-8')).hexdigest()[:12]


def width_gap(query):
    """True when a @media query's width conditions exclude every sample width."""
    mins = [int(x) for x in re.findall(r'min-width:\s*(\d+)px', query)]
    maxs = [int(x) for x in re.findall(r'max-width:\s*(\d+)px', query)]
    if not mins and not maxs:
        return False
    return not any(all(w >= v for v in mins) and all(w <= v for v in maxs)
                   for w in SAMPLE_WIDTHS)


def always_any(u):
    """Mirror the harness: a rule with ANY always-include selector is added
    to every probed page unconditionally, so it never needs probing."""
    return any(test_selector(s) is None for s in u['selectors'])


def hard_tokens(sel):
    """Class/id tokens a page must contain for this selector to match.
    Tokens inside functional pseudo-classes (:not/:is/:where/...) are dropped:
    :not() tokens are not requirements, :is() tokens are any-of. Fewer tokens
    means broader candidacy — always the safe direction."""
    s, prev = sel, None
    while prev != s:
        prev, s = s, PSEUDO_FN.sub('', s)
    return {m.group(1) for m in CLASS_ID_TOKEN.finditer(s)}


def load_page_texts():
    """Page HTML with the inline critical block stripped — its CSS text would
    otherwise satisfy token searches for the very selectors being tested."""
    pages = json.loads((FLAT / 'pages.json').read_text())
    return {p: CRITICAL_RE.sub('', (ROOT / p.lstrip('/'))
                               .read_text(encoding='utf-8'))
            for p in pages}


def js_token_blob():
    """First-party JS concatenated: classes added at runtime (is-active,
    compact-card--selected, ...) live here, not in the HTML."""
    return '\n'.join(f.read_text(encoding='utf-8')
                     for f in sorted(ROOT.glob('*.js')))


def candidate_pages(u, page_texts, js_blob):
    """Pages this rule could possibly match, by static token presence."""
    cands = set()
    for sel in u['selectors']:
        toks = hard_tokens(sel)
        if not toks:
            return set(page_texts)          # unfilterable: everywhere
        req = [t for t in toks if t not in js_blob]
        if not req:
            return set(page_texts)          # all tokens script-added
        cands |= {p for p, txt in page_texts.items()
                  if all(t in txt for t in req)}
    return cands


def load_map():
    if not MAP_FILE.exists():
        return None
    return json.loads(MAP_FILE.read_text())


def save_map(m):
    m['universe'] = sorted(set(m['universe']))
    m['pages'] = {p: sorted(set(ks)) for p, ks in sorted(m['pages'].items())}
    MAP_FILE.write_text(json.dumps(m, indent=0, sort_keys=True))


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
        out.append({'id': u['id'], 'key': u['key'], 'sheet': u['sheet'],
                    'context': u['context'], 'gap': gap,
                    'tests': tests, 'always': always})
    RULES_FILE.write_text(json.dumps(out))

    crit_map = load_map()
    all_pages = json.loads((FLAT / 'pages.json').read_text())
    if crit_map is None:
        PROBE_FILE.write_text(json.dumps(sorted(all_pages)))
        print(f'{len(out)} rules exported; no critical_map.json — FULL probe '
              f'of {len(all_pages)} pages: open /System/flatten/critical.html '
              'and run `await runCritical()` (results auto-post to the sink)')
        return

    universe = set(crit_map['universe'])
    new_units = [u for u in units
                 if u['kind'] == 'rule' and u['key'] not in universe]
    probe = {p for p in all_pages if p not in crit_map['pages']}
    n_auto = 0
    if new_units:
        page_texts = load_page_texts()
        js_blob = js_token_blob()
        for u in new_units:
            if always_any(u):
                n_auto += 1
                continue
            probe |= candidate_pages(u, page_texts, js_blob)
    PROBE_FILE.write_text(json.dumps(sorted(probe)))
    if probe:
        print(f'{len(out)} rules exported; {len(new_units)} new/changed '
              f'({n_auto} always-include) -> {len(probe)} page(s) need '
              'probing: open /System/flatten/critical.html and run '
              '`await runCritical()` (results auto-post to the sink)')
    else:
        print(f'{len(out)} rules exported; {len(new_units)} new/changed, '
              '0 pages need probing — run `critical_css.py apply` directly')


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


def reconcile_map(units):
    """Ingest any fresh harness output, account for every current rule key,
    and return the up-to-date map. Exits with instructions when a new rule
    still needs pages probed."""
    all_pages = json.loads((FLAT / 'pages.json').read_text())
    snapshot = json.loads(RULES_FILE.read_text()) if RULES_FILE.exists() else []
    if snapshot and 'key' not in snapshot[0]:
        raise SystemExit('critical_rules.json predates the incremental map — '
                         'run `critical_css.py export` first')
    # the snapshot must describe the CURRENT css, or harness ids mean nothing
    current = [(u['id'], u['key']) for u in units if u['kind'] == 'rule']
    snap_ok = [(r['id'], r['key']) for r in snapshot] == current

    crit_map = load_map()
    ids_hash = (hashlib.sha1(IDS_FILE.read_bytes()).hexdigest()
                if IDS_FILE.exists() else None)
    id2key = {r['id']: r['key'] for r in snapshot}

    probed_now = set()
    if crit_map is None:
        # bootstrap: requires one FULL harness run against the current css
        if not snap_ok:
            raise SystemExit('critical_rules.json is stale — run export, then '
                             'the harness, then apply')
        ids_by_page = json.loads(IDS_FILE.read_text())
        missing = [p for p in all_pages if p not in ids_by_page]
        if missing:
            raise SystemExit(f'bootstrap needs a full harness run; '
                             f'{len(missing)} page(s) missing from '
                             f'critical_ids.json (e.g. {missing[0]})')
        crit_map = {'universe': [r['key'] for r in snapshot],
                    'pages': {p: sorted({id2key[i] for i in ids})
                              for p, ids in ids_by_page.items()},
                    'last_probe': ids_hash}
        print(f'bootstrapped critical_map.json from a full run '
              f'({len(all_pages)} pages, {len(snapshot)} rules)')
        return crit_map

    if ids_hash and ids_hash != crit_map.get('last_probe'):
        if not snap_ok:
            raise SystemExit('critical_ids.json was produced against a stale '
                             'export — run export + harness again')
        ids_by_page = json.loads(IDS_FILE.read_text())
        for page, ids in ids_by_page.items():
            crit_map['pages'][page] = sorted({id2key[i] for i in ids})
        crit_map['last_probe'] = ids_hash
        probed_now = set(ids_by_page)
        if probed_now:
            print(f'ingested harness results for {len(probed_now)} page(s)')

    universe = set(crit_map['universe'])
    pending = [u for u in units
               if u['kind'] == 'rule' and u['key'] not in universe]
    if pending:
        page_texts = load_page_texts()
        js_blob = js_token_blob()
        unresolved = {}
        for u in pending:
            if always_any(u):
                # mirror the harness: included on every page, no probe needed
                for p in crit_map['pages']:
                    crit_map['pages'][p].append(u['key'])
                universe.add(u['key'])
                continue
            cands = candidate_pages(u, page_texts, js_blob)
            if cands <= probed_now:
                universe.add(u['key'])       # probed or statically impossible
            else:
                unresolved[u['key']] = cands - probed_now
        if unresolved:
            need = sorted(set().union(*unresolved.values()))
            raise SystemExit(
                f'{len(unresolved)} new rule(s) need probing on '
                f'{len(need)} page(s) — run `critical_css.py export`, then '
                'the harness, then apply again')
    never = [p for p in all_pages if p not in crit_map['pages']]
    if never:
        raise SystemExit(f'{len(never)} page(s) never probed '
                         f'(e.g. {never[0]}) — run export + harness')
    crit_map['universe'] = sorted(universe)
    return crit_map


def cmd_apply():
    units = source_rules()
    crit_map = reconcile_map(units)
    all_pages = json.loads((FLAT / 'pages.json').read_text())
    css_texts = {name: (ROOT / name).read_text(encoding='utf-8')
                 for name in SOURCES}
    cache = {}
    n = 0
    for page in sorted(all_pages):
        page_keys = set(crit_map['pages'][page])
        ids = [u['id'] for u in units
               if u['kind'] == 'rule' and u['key'] in page_keys]
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
            text = re.sub(r'[ \t]*' + re.escape(blog_link.group(0)) + r'\n?',
                          '', text)
        text = LINK_RE.sub(lambda m: block if m.group('file') == 'style'
                           else m.group(0), text, count=len(links))
        p.write_text(text, encoding='utf-8')
        n += 1
    save_map(crit_map)
    PROBE_FILE.unlink(missing_ok=True)
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
