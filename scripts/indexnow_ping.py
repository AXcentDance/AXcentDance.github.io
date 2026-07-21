#!/usr/bin/env python3
"""
Pings IndexNow (Bing, DuckDuckGo, Yandex, Seznam, Naver) with the URLs whose
HTML changed between two commits. Google does not participate in IndexNow;
this exists purely for the other engines. Called by
.github/workflows/update-sitemap.yml after each push to main.

Only genuinely changed, indexable URLs are submitted: engines throttle keys
that repeatedly submit unchanged pages, the same way Google discounts
untrustworthy sitemap lastmod dates.

Usage: python3 scripts/indexnow_ping.py <before-sha> <after-sha> [--dry-run]

A failed ping must never break the deploy workflow, so this script always
exits 0.
"""

import json
import os
import subprocess
import sys
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from generate_sitemap_final import DOMAIN, get_url_path, is_noindex

API_ENDPOINT = 'https://api.indexnow.org/indexnow'
# Public by design; must match the <KEY>.txt file at the site root.
KEY = 'c27aefe02e8179db6731d8dc7b1d2f70'
HOST = DOMAIN.split('//', 1)[1]
ZERO_SHA = '0' * 40
# Mirrors the directories generate_sitemap_final.py excludes from the sitemap.
EXCLUDED_DIRS = ('scripts/', 'assets/', 'System/', 'tests/', 'node_modules/',
                 '.git/', '.github/', '.claude/', '.agent/')
MAX_URLS_PER_REQUEST = 10000


def run_git(args):
    result = subprocess.run(['git'] + args, cwd=ROOT_DIR,
                            capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def changed_html_files(before, after):
    """HTML files added/copied/modified/renamed in the commit range."""
    diff = None
    if before and before != ZERO_SHA:
        diff = run_git(['diff', '--name-only', '--diff-filter=ACMR',
                        before, after, '--', '*.html'])
    if diff is None:
        # Branch creation or unreachable before-sha (force push): fall back
        # to the last commit only.
        diff = run_git(['diff', '--name-only', '--diff-filter=ACMR',
                        f'{after}~1', after, '--', '*.html'])
    if diff is None:
        return []
    return [line for line in diff.splitlines() if line]


def indexable_urls(rel_paths):
    urls = set()
    for rel_path in rel_paths:
        if rel_path.startswith(EXCLUDED_DIRS):
            continue
        filepath = os.path.join(ROOT_DIR, rel_path)
        if not os.path.isfile(filepath) or is_noindex(filepath):
            continue
        urls.add(DOMAIN + get_url_path(filepath))
    return sorted(urls)


def ping(urls, dry_run):
    payload = {'host': HOST, 'key': KEY, 'urlList': urls}
    if dry_run:
        print("Dry run; would submit:")
        print(json.dumps(payload, indent=2))
        return
    request = urllib.request.Request(
        API_ENDPOINT,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"IndexNow responded {response.status} "
                  f"for {len(urls)} URL(s).")
    except Exception as e:
        print(f"IndexNow ping failed (non-fatal): {e}")


def main():
    dry_run = '--dry-run' in sys.argv[1:]
    shas = [a for a in sys.argv[1:] if a != '--dry-run']
    if len(shas) != 2:
        print("usage: indexnow_ping.py <before-sha> <after-sha> [--dry-run]")
        return
    urls = indexable_urls(changed_html_files(shas[0], shas[1]))
    if not urls:
        print("No indexable URL changes; nothing to submit.")
        return
    ping(urls[:MAX_URLS_PER_REQUEST], dry_run)


if __name__ == '__main__':
    main()
