"""Rendered-truth gate for responsive image `sizes` attributes.

Loads every page that carries `img[srcset][sizes]` in headless Chrome, measures each
image's rendered width at 375 / 768 / 1440 CSS px inside a same-origin, script-less
sandboxed iframe, and compares it against the `sizes` slot the browser would resolve.
A mismatch counts as a failure only when it flips which srcset candidate gets fetched
at DPR 1 or DPR 2 (a "bucket flip") — px drift that never changes the fetched file is
tolerated by design.

The iframe deliberately blocks page JavaScript (sandbox without allow-scripts): layout
on this site is CSS-driven, scripts only animate opacity/transform, and a script-free
frame keeps the measurement deterministic (no GSAP/Three/HLS timers).

Usage:
    python3 scripts/sizes_truth_checker.py                 # validate the whole site
    python3 scripts/sizes_truth_checker.py --pages a.html de/a.html
    python3 scripts/sizes_truth_checker.py --bless         # validate, then write the
                                                           # manifest site_health enforces

The blessed manifest (scripts/data/sizes_manifest.json) records every instance's
`sizes` string. site_health.py statically fails any page whose current attribute
differs from the manifest, forcing this checker to be re-run after layout or
attribute changes. Run this gate whenever CSS layout or image markup changes.
"""

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_health import (  # noqa: E402  (shared static helpers live in the gate)
    EXCLUDED_DIRS, MANIFEST_PATH, ROOT_DIR, STUB_DIRS, iter_size_imgs,
)

VIEWPORTS = [(375, 812), (768, 1024), (1440, 900)]
BATCH_SIZE = 12
MAX_CHROME = 4
# Wall-clock cap per batch. Chrome is killed as soon as the harness POSTs its
# results — macOS Chrome never exits cleanly on its own (bundled updater).
CHROME_TIMEOUT = 120

HARNESS_ROUTE = '/__sizes_harness__'
RESULT_ROUTE = '/__sizes_result__'

HARNESS_TEMPLATE = """<!DOCTYPE html>
<meta charset="utf-8">
<title>sizes harness</title>
<style>body{margin:0}iframe{border:0;display:block}</style>
<iframe id="f" sandbox="allow-same-origin"></iframe>
<pre id="out"></pre>
<script>
const PAGES = __PAGES__;
const VIEWPORTS = __VIEWPORTS__;
const frame = document.getElementById('f');
const rows = [];

function load(src) {
    return new Promise((resolve) => {
        frame.onload = () => resolve();
        frame.src = src;
    });
}

function settle(win) {
    return new Promise((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(resolve));
    });
}

function resolveSlot(win, sizes) {
    for (const part of sizes.split(',').map((s) => s.trim())) {
        const m = part.match(/^\\((.+)\\)\\s+(\\S+)$/);
        if (m) {
            if (win.matchMedia('(' + m[1] + ')').matches) return m[2];
        } else {
            return part; // unconditioned default (last entry)
        }
    }
    return null;
}

function probe(page, vw) {
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const imgs = doc.querySelectorAll('img[sizes][srcset]');
    imgs.forEach((img, idx) => {
        const w = img.offsetWidth;
        const sizes = img.getAttribute('sizes');
        const slot = resolveSlot(win, sizes);
        let slotPx = null;
        if (slot) {
            slotPx = slot.endsWith('vw')
                ? (parseFloat(slot) * vw) / 100
                : parseFloat(slot);
        }
        rows.push({
            page: page,
            vw: vw,
            idx: idx,
            src: (img.getAttribute('src') || '').split('/').pop(),
            srcset: img.getAttribute('srcset'),
            sizes: sizes,
            w: w,
            slotPx: slotPx === null ? null : Math.round(slotPx * 10) / 10,
        });
    });
}

(async () => {
    let error = null;
    try {
        for (const page of PAGES) {
            await load('/' + page + '?__probe');
            for (const [vw, vh] of VIEWPORTS) {
                frame.style.width = vw + 'px';
                frame.style.height = vh + 'px';
                await settle(frame.contentWindow);
                probe(page, vw);
            }
        }
    } catch (e) {
        error = String(e);
    }
    await fetch('__RESULT_URL__', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: error, rows: rows }),
    });
    document.title = 'HARNESS-DONE';
})();
</script>
"""


def find_chrome():
    candidates = [os.environ.get('CHROME_BIN')]
    candidates += ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
    for c in candidates:
        if c and shutil.which(c):
            return shutil.which(c)
    for mac_path in (
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ):
        if os.path.exists(mac_path):
            return mac_path
    return None


def collect_target_pages(only=None):
    """Pages (rel paths) that contain at least one img[srcset][sizes]."""
    targets = []
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            r = os.path.relpath(os.path.join(root, f), ROOT_DIR).replace(os.sep, '/')
            if any(r == s or r.startswith(s + '/') for s in STUB_DIRS):
                continue
            if only is not None and r not in only:
                continue
            with open(os.path.join(root, f), encoding='utf-8') as fh:
                content = fh.read()
            if iter_size_imgs(content):
                targets.append(r)
    return targets


class HarnessHandler(SimpleHTTPRequestHandler):
    harnesses = {}
    results = {}
    events = {}

    def do_GET(self):
        path = self.path.split('?')[0]
        if path.startswith(HARNESS_ROUTE):
            body = self.harnesses.get(path)
            if body is None:
                self.send_error(404)
                return
            data = body.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()

    def do_POST(self):
        path = self.path.split('?')[0]
        if path.startswith(RESULT_ROUTE):
            batch_id = path.rsplit('/', 1)[-1]
            length = int(self.headers.get('Content-Length', 0))
            self.results[batch_id] = self.rfile.read(length).decode('utf-8')
            self.send_response(204)
            self.end_headers()
            event = self.events.get(batch_id)
            if event:
                event.set()
            return
        self.send_error(404)

    def log_message(self, *args):
        pass


class QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # Chrome gets SIGKILLed the moment its batch reports back; in-flight
        # asset fetches then die as broken pipes — expected, not noteworthy.
        pass


def start_server():
    handler = partial(HarnessHandler, directory=ROOT_DIR)
    server = QuietServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def run_batch(chrome, port, batch_id, pages):
    bid = str(batch_id)
    route = f'{HARNESS_ROUTE}/{bid}.html'
    HarnessHandler.harnesses[route] = (
        HARNESS_TEMPLATE
        .replace('__PAGES__', json.dumps(pages))
        .replace('__VIEWPORTS__', json.dumps(VIEWPORTS))
        .replace('__RESULT_URL__', f'{RESULT_ROUTE}/{bid}')
    )
    event = threading.Event()
    HarnessHandler.events[bid] = event
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            chrome, '--headless', '--disable-gpu', '--hide-scrollbars',
            '--no-first-run', '--no-default-browser-check', '--mute-audio',
            '--disable-background-networking', '--disable-component-update',
            f'--user-data-dir={profile}',
            '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1',
            f'http://127.0.0.1:{port}{route}',
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            done = event.wait(CHROME_TIMEOUT)
        finally:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
    if not done:
        raise RuntimeError(f'batch {bid} ({len(pages)} pages) timed out after {CHROME_TIMEOUT}s')
    payload = json.loads(HarnessHandler.results.pop(bid))
    if payload.get('error'):
        raise RuntimeError(f'batch {bid} harness error: {payload["error"]}')
    return payload['rows']


def pick_candidate(widths, need_px):
    """Smallest srcset width descriptor covering need_px, else the largest."""
    for w in sorted(widths):
        if w >= need_px:
            return w
    return max(widths)


def analyze(rows):
    """Returns (fd_rows, measured_pages). fd = file-choice divergence at DPR 1 or 2."""
    fd_rows = []
    measured_pages = set()
    for r in rows:
        measured_pages.add(r['page'])
        if not r['w'] or r['slotPx'] is None:
            continue  # hidden at this viewport, or unparseable slot
        widths = [int(m) for m in re.findall(r'\s(\d+)w', r['srcset'] or '')]
        if not widths:
            continue
        fd1 = pick_candidate(widths, r['w']) != pick_candidate(widths, r['slotPx'])
        fd2 = pick_candidate(widths, 2 * r['w']) != pick_candidate(widths, 2 * r['slotPx'])
        if fd1 or fd2:
            fd_rows.append({**r, 'fd1': fd1, 'fd2': fd2})
    return fd_rows, measured_pages


def build_manifest(pages):
    """Static manifest of every sizes-img instance, keyed page::src-basename::occurrence."""
    manifest = {}
    for page in pages:
        with open(os.path.join(ROOT_DIR, page), encoding='utf-8') as fh:
            content = fh.read()
        seen = {}
        for src, sizes, _ in iter_size_imgs(content):
            base = src.split('/')[-1]
            n = seen.get(base, 0)
            seen[base] = n + 1
            manifest[f'{page}::{base}::{n}'] = sizes
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--pages', nargs='*', help='restrict to these repo-relative pages')
    ap.add_argument('--bless', action='store_true',
                    help='on a clean full run, write scripts/data/sizes_manifest.json')
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print('FAIL: no Chrome/Chromium binary found (set CHROME_BIN).')
        sys.exit(2)

    only = set(args.pages) if args.pages else None
    targets = collect_target_pages(only)
    if only:
        missing = only - set(targets)
        for p in sorted(missing):
            print(f'  note: {p} skipped (no img[srcset][sizes] or not found)')
    if not targets:
        print('No pages with img[srcset][sizes] found.')
        sys.exit(0)
    if args.bless and only:
        print('FAIL: --bless requires a full run (no --pages).')
        sys.exit(2)

    server, port = start_server()
    print(f'sizes truth check: {len(targets)} pages x {len(VIEWPORTS)} viewports '
          f'(chrome: {os.path.basename(chrome)}, port {port})')

    batches = [targets[i:i + BATCH_SIZE] for i in range(0, len(targets), BATCH_SIZE)]
    rows, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CHROME) as pool:
        futures = {
            pool.submit(run_batch, chrome, port, i, batch): batch
            for i, batch in enumerate(batches)
        }
        for fut in concurrent.futures.as_completed(futures):
            try:
                rows.extend(fut.result())
            except Exception as e:  # noqa: BLE001 - report and fail below
                errors.append(str(e))
    server.shutdown()

    fd_rows, measured = analyze(rows)
    unmeasured = sorted(set(targets) - measured)

    print('-' * 78)
    if fd_rows:
        print(f'{"page":<44} {"vw":>4} {"rendered":>8} {"slot":>7}  flip  src')
        for r in sorted(fd_rows, key=lambda r: (r['page'], r['vw'], r['idx'])):
            flip = ('1x' if r['fd1'] else '') + ('2x' if r['fd2'] else '')
            print(f'{r["page"]:<44} {r["vw"]:>4} {r["w"]:>8} {r["slotPx"]:>7}  '
                  f'{flip:<4}  {r["src"]}')
        print('-' * 78)
    for e in errors:
        print(f'  ERROR {e}')
    for p in unmeasured:
        print(f'  ERROR no measurements returned for {p}')

    if fd_rows or errors or unmeasured:
        print(f'FAIL: {len(fd_rows)} file-choice divergence(s), '
              f'{len(errors) + len(unmeasured)} error(s). '
              f'Fix the sizes attributes (or layout), then re-run; '
              f'bless with --bless once clean.')
        sys.exit(1)

    print(f'PASS: {len(rows)} measurements, zero file-choice divergences.')
    if args.bless:
        manifest = build_manifest(targets)
        os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as fh:
            json.dump(manifest, fh, indent=1, sort_keys=True)
            fh.write('\n')
        print(f'Blessed {len(manifest)} instances -> {os.path.relpath(MANIFEST_PATH, ROOT_DIR)}')


if __name__ == '__main__':
    main()
