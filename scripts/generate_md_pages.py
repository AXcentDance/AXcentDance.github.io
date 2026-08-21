#!/usr/bin/env python3
"""Markdown twins: a .md rendition of every indexable page, next to its HTML.

Agent readiness (2026-08-21). GitHub Pages serves .md files with
Content-Type: text/markdown; charset=utf-8, so publishing a twin per page
gives AI agents a clean markdown rendition at a predictable URL: append .md
to any clean page URL (https://axcentdance.com/schedule -> /schedule.md; use
/index.md for the homepage and /blog/index.md for section indexes). Full
Accept-header content negotiation additionally needs the edge worker
described in System/agent-readiness.md; the twins are its data source.

Each twin contains the page title, meta description, canonical URL, language
links, and the <main> content converted to structured markdown (headings,
paragraphs, lists, links resolved to absolute clean URLs).

Usage:
  python3 scripts/generate_md_pages.py           regenerate all twins
  python3 scripts/generate_md_pages.py --check   freshness gate (site_health):
                                                 every indexable page must have
                                                 a byte-current twin, and no
                                                 orphaned twin may remain
"""
import os
import re
import sys

from bs4 import BeautifulSoup, NavigableString, Tag

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_health  # noqa: E402  (shared page collection + noindex logic)

ROOT_DIR = site_health.ROOT_DIR
DOMAIN = site_health.DOMAIN

# Tags whose subtrees never contribute content
STRIP_TAGS = ('script', 'style', 'noscript', 'iframe', 'svg', 'template',
              'form', 'button', 'video', 'audio', 'picture', 'img', 'dialog')
HEADING_RE = re.compile(r'^h([1-6])$')
# A twin is recognizable by this header line; any .md without it (README,
# AGENTS.md, project_rules.md, future hand-written docs) is never touched
TWIN_MARKER = '- Agent guide: https://axcentdance.com/llms.txt'

# Page map used for internal link resolution; populated by expected_twins()
# (tests may inject their own fixture map)
PAGES = {}


def collapse(text):
    return re.sub(r'\s+', ' ', text).strip()


def clean_url(href, page_rel):
    """Absolute clean URL for an internal href; external hrefs unchanged."""
    target = site_health.resolve_href(page_rel, href, PAGES)
    if target is None:
        if href.startswith(('http://', 'https://')):
            return href
        return None
    path = '/' + target[:-5] if target.endswith('.html') else '/' + target
    if path.endswith('/index'):
        path = path[:-5]
    return DOMAIN + path


def inline_text(node, page_rel):
    """Inline rendering: plain text with <a> converted to markdown links."""
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ''
    if node.name in STRIP_TAGS:
        return ''
    if node.name == 'a':
        label = collapse(''.join(inline_text(c, page_rel)
                                 for c in node.children))
        href = node.get('href', '')
        if not label:
            return ''
        if not href or href.startswith(('#', 'javascript:')):
            return label
        url = clean_url(href, page_rel)
        return f'[{label}]({url})' if url else label
    if node.name == 'br':
        return ' '
    return ''.join(inline_text(c, page_rel) for c in node.children)


def block_lines(node, page_rel, depth=0):
    """Recursive block rendering to markdown lines."""
    lines = []
    if isinstance(node, NavigableString) or not isinstance(node, Tag):
        return lines
    if node.name in STRIP_TAGS or node.get('aria-hidden') == 'true':
        return lines
    m = HEADING_RE.match(node.name)
    if m:
        text = collapse(inline_text(node, page_rel))
        if text:
            lines.append('#' * int(m.group(1)) + ' ' + text)
        return lines
    if node.name in ('p', 'figcaption', 'blockquote', 'summary', 'dt', 'dd',
                     'address'):
        text = collapse(inline_text(node, page_rel))
        if text:
            prefix = '> ' if node.name == 'blockquote' else ''
            lines.append(prefix + text)
        return lines
    if node.name == 'li':
        text = collapse(inline_text(node, page_rel))
        nested = []
        for child in node.children:
            if isinstance(child, Tag) and child.name in ('ul', 'ol'):
                nested.extend(block_lines(child, page_rel, depth + 1))
        if text:
            lines.append('  ' * depth + '- ' + text)
        lines.extend(nested)
        return lines
    if node.name in ('ul', 'ol'):
        for child in node.children:
            lines.extend(block_lines(child, page_rel, depth))
        return lines
    if node.name == 'a':
        text = collapse(inline_text(node, page_rel))
        if text:
            lines.append(text)
        return lines
    if node.name in ('table',):
        for row in node.find_all('tr'):
            cells = [collapse(inline_text(c, page_rel))
                     for c in row.find_all(('th', 'td'))]
            if any(cells):
                lines.append('| ' + ' | '.join(cells) + ' |')
        return lines
    # generic container: recurse; leaf spans/divs with bare text become lines
    child_lines = []
    for child in node.children:
        child_lines.extend(block_lines(child, page_rel, depth))
    if child_lines:
        return child_lines
    if node.name in ('div', 'span', 'section', 'article', 'main', 'aside',
                     'header', 'footer', 'label', 'a', 'strong', 'em', 'time'):
        text = collapse(inline_text(node, page_rel))
        if text:
            lines.append(text)
    return lines


def dedupe(lines):
    """Drop consecutive duplicate lines (repeated card labels etc.)."""
    out = []
    for line in lines:
        if not out or out[-1] != line:
            out.append(line)
    return out


def render_page(page_rel, content):
    soup = BeautifulSoup(content, 'html.parser')
    title = collapse(soup.title.string) if soup.title and soup.title.string \
        else page_rel
    meta = soup.find('meta', attrs={'name': 'description'})
    desc = collapse(meta['content']) if meta and meta.get('content') else ''
    canonical = ''
    link = soup.find('link', rel='canonical')
    if link and link.get('href'):
        canonical = link['href'].strip()
    lang = 'de' if page_rel.startswith('de/') else 'en'
    alt = ''
    for l in soup.find_all('link', rel='alternate'):
        hreflang = l.get('hreflang')
        if hreflang and hreflang != 'x-default' and hreflang != lang \
                and l.get('href'):
            alt = f"{hreflang}: {l['href'].strip()}"
            break

    head = [f'# {title}', '']
    if desc:
        head += [f'> {desc}', '']
    if canonical:
        head.append(f'- Canonical (HTML): {canonical}')
    head.append(f'- Language: {lang}')
    if alt:
        head.append(f'- Translation ({alt.split(":", 1)[0]}):'
                    f'{alt.split(":", 1)[1]}')
    head.append(f'- Agent guide: {DOMAIN}/llms.txt')
    head += ['', '---', '']

    main = soup.find('main') or soup.body or soup
    body = dedupe(block_lines(main, page_rel))
    text = '\n'.join(head) + '\n\n'.join(body)
    return text.rstrip() + '\n'


def twin_path(page_rel):
    return page_rel[:-5] + '.md'


def expected_twins():
    """{twin_rel: rendered_markdown} for every indexable page."""
    global PAGES
    PAGES = site_health.collect_pages()
    indexable = {p for p, c in PAGES.items() if not site_health.is_noindex(c)}
    return {twin_path(p): render_page(p, PAGES[p]) for p in sorted(indexable)}


def is_twin_file(path):
    """Only a file carrying the generated-twin marker counts as a twin.
    Hand-written .md files (README.md, AGENTS.md, ...) are never touched."""
    try:
        with open(path, encoding='utf-8') as f:
            head = f.read(2000)
    except OSError:
        return False
    return TWIN_MARKER in head


def existing_twins(expected):
    """Twin .md files currently on disk in the page directories."""
    dirs = {os.path.dirname(t) for t in expected}
    found = set()
    for d in sorted(dirs):
        full = os.path.join(ROOT_DIR, d) if d else ROOT_DIR
        for f in sorted(os.listdir(full)):
            if not f.endswith('.md'):
                continue
            r = os.path.join(d, f).replace(os.sep, '/') if d else f
            if is_twin_file(os.path.join(ROOT_DIR, r)):
                found.add(r)
    return found


def cmd_generate():
    expected = expected_twins()
    written = unchanged = 0
    for twin, text in expected.items():
        path = os.path.join(ROOT_DIR, twin)
        old = None
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                old = f.read()
        if old == text:
            unchanged += 1
            continue
        if old is not None and TWIN_MARKER not in old:
            print(f'SKIP {twin}: existing file is not a generated twin '
                  '(refusing to overwrite a hand-written .md)')
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        written += 1
    removed = 0
    for orphan in sorted(existing_twins(expected) - set(expected)):
        os.remove(os.path.join(ROOT_DIR, orphan))
        print(f'removed orphaned twin: {orphan}')
        removed += 1
    print(f'markdown twins: {written} written, {unchanged} unchanged, '
          f'{removed} removed ({len(expected)} total)')


def cmd_check():
    expected = expected_twins()
    problems = []
    for twin, text in expected.items():
        path = os.path.join(ROOT_DIR, twin)
        if not os.path.exists(path):
            problems.append(f'{twin}: missing')
            continue
        with open(path, encoding='utf-8') as f:
            if f.read() != text:
                problems.append(f'{twin}: STALE (page changed since '
                                'generation)')
    for orphan in sorted(existing_twins(expected) - set(expected)):
        problems.append(f'{orphan}: orphaned twin (no indexable source page)')
    if problems:
        print('\n'.join(problems))
        print(f'FAIL: {len(problems)} markdown twin problem(s). '
              'Re-run: python3 scripts/generate_md_pages.py')
        sys.exit(1)
    print(f'PASS: markdown twins current ({len(expected)} pages).')


if __name__ == '__main__':
    if '--check' in sys.argv:
        cmd_check()
    else:
        cmd_generate()
