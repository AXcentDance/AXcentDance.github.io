#!/usr/bin/env python3
"""Generate (or verify) the minified twins of the site's first-party assets.

Pages ship the .min twins; the readable sources stay the editing surface.
After ANY edit to a source below, run this script, then bump the twin's ?v=
query in the pages that reference it.

    python3 scripts/minify_assets.py           # regenerate all twins
    python3 scripts/minify_assets.py --check   # verify twins are current (CI gate)

esbuild is pinned so local and CI runs produce byte-identical output.
--check re-minifies each source in memory and byte-compares with the twin on
disk; a missing or stale twin fails the gate. If npx/esbuild cannot run at
all (offline), the gate degrades to an mtime comparison so purely local,
non-asset work is not blocked — CI always has the real check.

script-blog.min.js is NOT generated here: it is the hand-frozen slim script
that blog pages load instead of the full script.js (they need only the
header/menu behaviour). Do not overwrite it with a minified script.js.
"""

import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESBUILD = 'esbuild@0.24.0'

# source -> minified twin shipped by the pages
ASSETS = {
    'style.css': 'style.min.css',
    'blog-post.css': 'blog-post.min.css',
    'script.js': 'script.min.js',
}


def minify(source_path):
    """Return minified bytes for a source file, or None if esbuild is unavailable."""
    try:
        result = subprocess.run(
            ['npx', '-y', ESBUILD, source_path, '--minify'],
            cwd=ROOT_DIR, capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode('utf-8', 'replace'))
        raise SystemExit(f"esbuild failed on {source_path}")
    return result.stdout


def build():
    for source, twin in ASSETS.items():
        out = minify(source)
        if out is None:
            raise SystemExit('esbuild unavailable (npx download failed?) — cannot build')
        with open(os.path.join(ROOT_DIR, twin), 'wb') as f:
            f.write(out)
        src_kb = os.path.getsize(os.path.join(ROOT_DIR, source)) // 1024
        print(f"  {source} ({src_kb} KB) -> {twin} ({len(out) // 1024} KB)")
    print('PASS: minified twins regenerated.')


def check():
    stale = []
    degraded = False
    for source, twin in ASSETS.items():
        twin_path = os.path.join(ROOT_DIR, twin)
        source_path = os.path.join(ROOT_DIR, source)
        if not os.path.exists(twin_path):
            stale.append(f"{twin} missing (run scripts/minify_assets.py)")
            continue
        expected = minify(source)
        if expected is None:
            degraded = True
            if os.path.getmtime(twin_path) < os.path.getmtime(source_path):
                stale.append(f"{twin} older than {source} (run scripts/minify_assets.py)")
            continue
        with open(twin_path, 'rb') as f:
            if f.read() != expected:
                stale.append(f"{twin} stale vs {source} (run scripts/minify_assets.py)")
    if stale:
        for s in stale:
            print(f"  FAIL {s}")
        print('FAIL: minified twins out of date.')
        sys.exit(1)
    note = ' (esbuild unavailable — mtime check only)' if degraded else ''
    print(f'PASS: minified twins current{note}.')


if __name__ == '__main__':
    if '--check' in sys.argv:
        check()
    else:
        build()
