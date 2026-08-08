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

# Blessed by scripts/sizes_truth_checker.py --bless after an in-browser rendered-truth run
MANIFEST_PATH = os.path.join(ROOT_DIR, 'scripts', 'data', 'sizes_manifest.json')

IMG_TAG_RE = re.compile(r'<img\b[^>]*?>', re.S)

failures = []
warnings = []


def _attr(tag, name):
    """Double-quoted attribute value from a tag, whitespace-normalized, or None."""
    m = re.search(r'\b%s\s*=\s*"([^"]*)"' % name, tag, re.S)
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else None


def iter_size_imgs(content):
    """(src, sizes, srcset) for every img with a w-descriptor srcset AND a sizes attr."""
    out = []
    for tag in IMG_TAG_RE.findall(content):
        srcset = _attr(tag, 'srcset')
        if not srcset or not re.search(r'\s\d+w\b', srcset):
            continue
        sizes = _attr(tag, 'sizes')
        if sizes is None:
            continue
        out.append((_attr(tag, 'src') or '', sizes, srcset))
    return out


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


def check_speculation_rules(pages):
    """Every page must carry exactly one valid speculationrules prefetch block (hover prefetch)."""
    for page in sorted(pages):
        blocks = re.findall(r'<script type="speculationrules">(.*?)</script>', pages[page], re.S)
        if not blocks:
            fail('speculation', f"{page} is missing the speculationrules prefetch block")
            continue
        if len(blocks) > 1:
            fail('speculation', f"{page} has {len(blocks)} speculationrules blocks (expected 1)")
        for block in blocks:
            try:
                rules = json.loads(block)
            except ValueError as e:
                fail('speculation', f"{page}: invalid speculationrules JSON ({e})")
                continue
            if 'prefetch' not in rules:
                fail('speculation', f"{page}: speculationrules block has no prefetch rule")


def check_page_baseline(pages):
    """Every page ships exactly one CSP meta; every page with a header carries the
    skip link and its #main-content target (keyboard accessibility)."""
    for page in sorted(pages):
        content = pages[page]
        csp = re.findall(r'<meta\s+http-equiv=["\']Content-Security-Policy["\']', content, re.I)
        if not csp:
            fail('baseline', f"{page} is missing the Content-Security-Policy meta tag")
        elif len(csp) > 1:
            fail('baseline', f"{page} has {len(csp)} CSP meta tags (expected 1)")
        if re.search(r'<header\b', content, re.I):
            if 'class="skip-link"' not in content:
                fail('baseline', f"{page} has a header but no skip link (copy it from index.html)")
            elif 'id="main-content"' not in content:
                fail('baseline', f"{page} has a skip link but no id=\"main-content\" target")


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


def _srcset_shape(srcset):
    """Order-preserving (basename, descriptor) tuple — path-form agnostic."""
    shape = []
    for cand in srcset.split(','):
        parts = cand.strip().split()
        if not parts:
            continue
        shape.append((parts[0].split('/')[-1], ' '.join(parts[1:])))
    return tuple(shape)


def check_image_sizes(pages):
    """Responsive images must carry honest `sizes` values.

    Static tripwire for the in-browser gate (scripts/sizes_truth_checker.py): every
    img[srcset] needs a sizes attribute, imagesizes preload hints must mirror the img
    they preload (else the preload double-downloads), and each instance's sizes string
    must match the manifest blessed by the checker's rendered-truth run. Any new or
    edited attribute fails here until the checker re-verifies and re-blesses.
    """
    try:
        with open(MANIFEST_PATH, encoding='utf-8') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        manifest = None
        warn('img-sizes', 'sizes manifest missing - run: python3 scripts/sizes_truth_checker.py --bless')
    except ValueError as e:
        manifest = None
        fail('img-sizes', f'sizes manifest unreadable ({e})')

    current = {}
    for page in sorted(pages):
        content = pages[page]
        size_imgs = iter_size_imgs(content)

        for tag in IMG_TAG_RE.findall(content):
            srcset = _attr(tag, 'srcset')
            if srcset and re.search(r'\s\d+w\b', srcset) and _attr(tag, 'sizes') is None:
                name = (_attr(tag, 'src') or '?').split('/')[-1]
                fail('img-sizes', f'{page}: img "{name}" has a w-descriptor srcset but no sizes attribute')

        for link in re.findall(r'<link\b[^>]*?>', content, re.S):
            if _attr(link, 'rel') != 'preload' or _attr(link, 'as') != 'image':
                continue
            isizes = _attr(link, 'imagesizes')
            isrcset = _attr(link, 'imagesrcset')
            if not isizes or not isrcset:
                continue
            # preload hints may reference the AVIF twins of a webp img srcset
            twins = [s for _, s, ss in size_imgs
                     if _srcset_shape(ss) == _srcset_shape(isrcset.replace('.avif', '.webp'))]
            if not twins:
                warn('img-sizes', f'{page}: imagesizes preload matches no img srcset on the page')
            elif isizes not in twins:
                fail('img-sizes', f'{page}: imagesizes preload "{isizes}" does not match its '
                                  f'img sizes "{twins[0]}" (double-download risk)')

        seen = {}
        for src, sizes, _ in size_imgs:
            base = src.split('/')[-1]
            n = seen.get(base, 0)
            seen[base] = n + 1
            current[f'{page}::{base}::{n}'] = sizes

    if manifest is not None:
        for key in sorted(current):
            page, base, _ = key.split('::')
            blessed = manifest.get(key)
            if blessed is None:
                fail('img-sizes', f'{page}: responsive img "{base}" is not in the blessed manifest - '
                                  f'verify rendered truth: python3 scripts/sizes_truth_checker.py --bless')
            elif blessed != current[key]:
                fail('img-sizes', f'{page}: sizes for "{base}" changed (blessed "{blessed}", now '
                                  f'"{current[key]}") - re-verify: python3 scripts/sizes_truth_checker.py --bless')
        for key in sorted(set(manifest) - set(current)):
            warn('img-sizes', f'stale manifest entry (img gone): {key} - re-bless to prune')


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
    check_speculation_rules(pages)
    check_page_baseline(pages)
    check_titles_descriptions(pages, indexable)
    check_image_sizes(pages)
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
