import os
import re
import sys
import json
import subprocess
from urllib.parse import urlparse, unquote

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://axcentdance.com'

# Directories that are never public content
EXCLUDED_DIRS = {'.git', '.github', '.claude', '.agent', 'System', 'tests', 'scripts',
                 'assets', 'node_modules', '__pycache__', '.well-known', 'supabase'}
# Legacy redirect-stub trees (noindex by design, checked separately)
STUB_DIRS = {'blog-posts', os.path.join('de', 'blog-posts')}
# Indexable pages that legitimately have no inbound body/nav link
ORPHAN_EXEMPT = {'index.html', 'de/index.html'}

BLOG_FILTERS = {'all', 'music', 'tips', 'community', 'education', 'wellness', 'events'}

failures = []
warnings = []


def fail(section, msg):
    failures.append(f"[{section}] {msg}")


def warn(section, msg):
    warnings.append(f"[{section}] {msg}")


def rel(path):
    return os.path.relpath(path, ROOT_DIR).replace(os.sep, '/')


def collect_pages():
    """Returns {rel_path: content} for every HTML page outside excluded dirs."""
    pages = {}
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            if f.endswith('.html'):
                p = os.path.join(root, f)
                r = rel(p)
                if any(r == s or r.startswith(s + '/') for s in STUB_DIRS):
                    continue
                with open(p, encoding='utf-8') as fh:
                    pages[r] = fh.read()
    return pages


def is_noindex(content):
    return re.search(r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex', content, re.I) is not None


def url_to_file(url_path, pages):
    """Maps a site-absolute clean-URL path to a repo file, or None."""
    path = unquote(url_path).strip()
    path = path.split('#')[0].split('?')[0]
    if not path or path == '/':
        return 'index.html'
    path = path.lstrip('/')
    if path.endswith('/'):
        path = path[:-1]
    for candidate in (path, path + '.html', path + '/index.html'):
        if candidate in pages:
            return candidate
    return None


def resolve_href(src_file, href, pages):
    """Resolves an internal href from a page to a repo file, or None if external/unresolvable."""
    href = href.strip()
    if not href or href.startswith(('mailto:', 'tel:', 'javascript:', 'data:')):
        return None
    if href.startswith('http'):
        u = urlparse(href)
        if u.netloc not in ('axcentdance.com', 'www.axcentdance.com'):
            return None
        return url_to_file(u.path, pages)
    if href.startswith('/'):
        return url_to_file(href, pages)
    if href.startswith('#'):
        return src_file
    base = os.path.dirname(src_file)
    joined = os.path.normpath(os.path.join(base, href.split('#')[0].split('?')[0])).replace(os.sep, '/')
    if joined in ('.', ''):
        joined = 'index.html'
    for candidate in (joined, joined + '.html', joined + '/index.html'):
        if candidate in pages:
            return candidate
    return None


def check_orphans(pages, indexable):
    inbound = {p: set() for p in indexable}
    for src, content in pages.items():
        if src not in indexable:
            continue
        for href in re.findall(r'href="([^"]+)"', content):
            target = resolve_href(src, href, pages)
            if target and target in inbound and target != src:
                inbound[target].add(src)
    for page, sources in sorted(inbound.items()):
        if not sources and page not in ORPHAN_EXEMPT:
            fail('orphans', f"{page} has no inbound link from any indexable page")


def check_sitemap(pages, indexable):
    sitemap_path = os.path.join(ROOT_DIR, 'sitemap.xml')
    if not os.path.exists(sitemap_path):
        fail('sitemap', 'sitemap.xml missing')
        return
    with open(sitemap_path, encoding='utf-8') as f:
        sm = f.read()
    locs = re.findall(r'<loc>([^<]+)</loc>', sm)
    loc_files = set()
    for loc in locs:
        u = urlparse(loc)
        target = url_to_file(u.path, pages)
        if target is None:
            fail('sitemap', f"sitemap URL has no matching file: {loc}")
        else:
            loc_files.add(target)
    for page in sorted(indexable):
        if page not in loc_files:
            fail('sitemap', f"indexable page missing from sitemap.xml: {page}")


def check_schema(pages, indexable):
    for page in sorted(indexable):
        content = pages[page]
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.S)
        if not blocks:
            warn('schema', f"{page} has no JSON-LD block")
            continue
        for block in blocks:
            try:
                json.loads(block)
            except ValueError as e:
                fail('schema', f"{page}: invalid JSON-LD ({e})")
                continue
            # Every site-URL @id must anchor to a real page or asset (catches phantom paths like /course/...)
            for id_url in set(re.findall(r'"@id":\s*"(%s[^"]*)"' % re.escape(DOMAIN), block)):
                base = id_url.split('#')[0]
                path = urlparse(base).path
                if path in ('', '/'):
                    continue
                if url_to_file(path, pages) is not None:
                    continue
                if os.path.isfile(os.path.join(ROOT_DIR, path.lstrip('/'))):
                    continue  # e.g. ImageObject @id anchored on the image file
                fail('schema', f"{page}: @id anchored to nonexistent URL: {id_url}")
            # Enum and date-format conventions
            for mode in set(re.findall(r'"courseMode":\s*"([^"]*)"', block)):
                if mode not in ('Onsite', 'Online', 'Blended'):
                    fail('schema', f"{page}: invalid courseMode \"{mode}\"")
            # dateModified: blog convention is date-only; static pages may use full ISO with offset
            for d in set(re.findall(r'"dateModified":\s*"([^"]*)"', block)):
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})?', d):
                    fail('schema', f"{page}: malformed dateModified \"{d}\"")
            for key in ('datePublished', 'startDate', 'endDate'):
                for d in set(re.findall(r'"%s":\s*"([^"]*)"' % key, block)):
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}', d):
                        fail('schema', f"{page}: {key} must be full ISO 8601 with offset, got \"{d}\"")


def check_canonicals(pages, indexable):
    for page in sorted(pages):
        content = pages[page]
        m = re.search(r'<link rel="canonical" href="([^"]+)"', content)
        if page in indexable:
            if not m:
                fail('canonical', f"{page} has no canonical")
                continue
            target = url_to_file(urlparse(m.group(1)).path, pages)
            if target is None:
                fail('canonical', f"{page} canonical points at nonexistent URL: {m.group(1)}")
            elif target != page:
                fail('canonical', f"{page} canonical resolves to a different page: {m.group(1)}")
        elif m:
            # noindex pages (redirect stubs) may canonicalize elsewhere, but never to a dead URL
            if url_to_file(urlparse(m.group(1)).path, pages) is None:
                fail('canonical', f"{page} (noindex) canonical points at nonexistent URL: {m.group(1)}")


def check_blog_indexes(pages, indexable):
    for index_file, prefix in (('blog/index.html', '/blog/'), ('de/blog/index.html', '/de/blog/')):
        if index_file not in pages:
            fail('blog', f"{index_file} missing")
            continue
        index_content = pages[index_file]
        blog_dir = os.path.dirname(index_file)
        for page in sorted(indexable):
            if os.path.dirname(page) != blog_dir or page == index_file:
                continue
            slug = os.path.basename(page)[:-5]
            if f'href="{prefix}{slug}"' not in index_content:
                fail('blog', f"{page} has no card on {index_file}")
        for cat in set(re.findall(r'data-category="([^"]+)"', index_content)):
            if cat not in BLOG_FILTERS:
                fail('blog', f"{index_file}: data-category \"{cat}\" matches no filter button")


def check_llms(pages):
    llms_path = os.path.join(ROOT_DIR, 'llms-full.txt')
    if not os.path.exists(llms_path):
        fail('llms', 'llms-full.txt missing')
        return
    with open(llms_path, encoding='utf-8') as f:
        content = f.read()
    for leak in ('.claude/', 'System/', 'blog-posts/', 'tests/'):
        if f'({leak}' in content:
            fail('llms', f"llms-full.txt leaks internal content: {leak}")


def check_titles_descriptions(pages, indexable):
    titles = {}
    descs = {}
    for page in sorted(indexable):
        content = pages[page]
        t = re.search(r'<title>(.*?)</title>', content, re.S)
        d = re.search(r'<meta\s+name="description"\s+content="(.*?)">', content, re.S)
        title = re.sub(r'\s+', ' ', t.group(1)).strip() if t else ''
        desc = re.sub(r'\s+', ' ', d.group(1)).strip() if d else ''
        if not title:
            fail('meta', f"{page} has no <title>")
        else:
            titles.setdefault(title, []).append(page)
            if not 50 <= len(title) <= 60:
                warn('meta', f"{page} title length {len(title)} (target 50-60): {title}")
        if not desc:
            fail('meta', f"{page} has no meta description")
        else:
            descs.setdefault(desc, []).append(page)
            if not 120 <= len(desc) <= 156:
                warn('meta', f"{page} description length {len(desc)} (target 120-156)")
    for title, ps in titles.items():
        if len(ps) > 1:
            fail('meta', f"duplicate title on {ps}: {title}")
    for desc, ps in descs.items():
        if len(ps) > 1:
            fail('meta', f"duplicate description on {ps}")


def run_external_checks():
    """Existing checkers with reliable pass/fail signals."""
    checks = [
        ('header/footer', ['python3', 'scripts/header_footer_checker.py'], 'PASS:'),
        ('headings', ['python3', 'scripts/heading_structure_checker.py'], 'issues: 0'),
        ('links', ['python3', 'scripts/check_broken_links.py'], 'No broken local links'),
        ('hreflang', ['python3', 'scripts/audit_hreflang.py'], 'perfectly reciprocal'),
    ]
    for name, cmd, ok_marker in checks:
        result = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
        if ok_marker not in result.stdout:
            tail = '\n'.join(result.stdout.strip().splitlines()[-8:])
            fail(name, f"checker did not pass:\n{tail}")

    # Breadcrumb audit flags files; only indexable ones count as failures
    result = subprocess.run(['python3', 'scripts/breadcrumb_audit.py'], cwd=ROOT_DIR,
                            capture_output=True, text=True)
    for flagged in re.findall(r'\[FILE\]\s+(\S+)', result.stdout):
        full = os.path.join(ROOT_DIR, flagged)
        if os.path.exists(full):
            with open(full, encoding='utf-8') as f:
                if not is_noindex(f.read()):
                    fail('breadcrumbs', f"{flagged} flagged by breadcrumb_audit")


def main():
    pages = collect_pages()
    indexable = {p for p, c in pages.items() if not is_noindex(c)}
    print(f"Site health check: {len(pages)} pages ({len(indexable)} indexable)")
    print("-" * 70)

    check_orphans(pages, indexable)
    check_sitemap(pages, indexable)
    check_schema(pages, indexable)
    check_canonicals(pages, indexable)
    check_blog_indexes(pages, indexable)
    check_llms(pages)
    check_titles_descriptions(pages, indexable)
    run_external_checks()

    for w in warnings:
        print(f"  WARN {w}")
    if warnings:
        print("-" * 70)
    if failures:
        for f in failures:
            print(f"  FAIL {f}")
        print("-" * 70)
        print(f"FAIL: {len(failures)} problem(s), {len(warnings)} warning(s).")
        sys.exit(1)
    print(f"PASS: all checks green ({len(warnings)} warning(s)).")


if __name__ == '__main__':
    main()
