#!/usr/bin/env python3
"""Rebuild palette-preview.html from index.html so the lab page IS the homepage.

The palette lab is a clone of the live homepage plus exactly four deltas:

  1. `<meta name="robots" content="noindex">`
  2. `<link rel="stylesheet" id="palette-css">` (the variant swap slot) and
     `palette-preview-enhancements.css` (preview-only composition layer)
  3. `palette-preview-page` on the body class list
  4. the `#palette-switcher` panel and its script before `</body>`

Everything else must track index.html byte for byte, otherwise the palettes are
being judged against a stale homepage. Run this after any homepage change:

    python3 scripts/rebuild_palette_preview.py

The switcher panel (the palette list itself) is preserved verbatim from the
current palette-preview.html, so edit the palette list there, not here. The
critical block is regenerated from index.html's rule set, since the two pages
share their above-the-fold markup and the switcher panel is inline-styled.

Responsive-image `sizes` are keyed per page in the blessed manifest, so a
homepage change that adds or moves images also needs:

    python3 scripts/sizes_truth_checker.py --bless
"""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import critical_css as cc  # noqa: E402

PAGE = 'palette-preview.html'
SWITCHER_START = '<div id="palette-switcher"'
NOSCRIPT_RE = re.compile(
    r'^[ \t]*<noscript><link rel="stylesheet" href="style\.min\.css\?v=[0-9.]+">'
    r'</noscript>\n', re.M)


def rebuild_markup():
    src = (ROOT / 'index.html').read_text(encoding='utf-8')
    old = (ROOT / PAGE).read_text(encoding='utf-8')

    # keep the owner-edited switcher panel verbatim
    switcher = old[old.index(SWITCHER_START):].split('\n</body>')[0]

    # 1. robots
    src, n = re.subn(r'<meta name="robots" content="[^"]*">',
                     '<meta name="robots" content="noindex">', src, count=1)
    assert n == 1, 'robots meta not found in index.html'

    # 2. palette stylesheet links, right after the async style.min.css noscript
    m = NOSCRIPT_RE.search(src)
    assert m and not NOSCRIPT_RE.search(src, m.end()), \
        'style.min.css noscript anchor missing or not unique'
    src = (src[:m.end()]
           + '  <link rel="stylesheet" id="palette-css">\n'
           + '  <link rel="stylesheet" href="palette-preview-enhancements.css">\n'
           + src[m.end():])

    # 3. body class
    src, n = re.subn(r'<body class="home-page nav-declutter">',
                     '<body class="home-page nav-declutter palette-preview-page">',
                     src, count=1)
    assert n == 1, 'homepage body tag not found'

    # 4. switcher panel
    assert src.count('\n</body>') == 1, '</body> not unique'
    src = src.replace('\n</body>', '\n' + switcher + '\n</body>', 1)

    (ROOT / PAGE).write_text(src, encoding='utf-8')


def refresh_critical():
    """Re-inline the critical block, reusing index.html's key set from the
    incremental map (critical_map.json, the pipeline of 2026-08-16)."""
    crit_map = cc.load_map()
    crit_map['pages']['/' + PAGE] = list(crit_map['pages']['/index.html'])
    cc.save_map(crit_map)

    units = cc.source_rules()
    keys = set(crit_map['pages']['/' + PAGE])
    ids = [u['id'] for u in units if u['kind'] == 'rule' and u['key'] in keys]
    css_texts = {name: (cc.ROOT / name).read_text(encoding='utf-8')
                 for name in cc.SOURCES}
    p = cc.ROOT / PAGE
    text = cc.NOSCRIPT_RE.sub('', cc.CRITICAL_RE.sub('', p.read_text(encoding='utf-8')))
    link = next(m for m in cc.LINK_RE.finditer(text) if m.group('file') == 'style')
    block_css = cc.minify_block(cc.assemble(units, ids))
    h = cc.page_hash(text, False, css_texts)
    block = (f'<style data-critical="{h}">{block_css}</style>\n    '
             + '\n    '.join(cc.async_links(link.group('prefix'),
                                            link.group('v'), None)))
    text = cc.LINK_RE.sub(lambda m: block if m.group('file') == 'style'
                          else m.group(0), text, count=1)
    p.write_text(text, encoding='utf-8')
    return h


if __name__ == '__main__':
    rebuild_markup()
    digest = refresh_critical()
    lines = (ROOT / PAGE).read_text(encoding='utf-8').count(os.linesep) + 1
    print(f'{PAGE} rebuilt from index.html ({lines} lines, critical {digest}). '
          'Run site_health.py; bless sizes if the homepage image set changed.')
