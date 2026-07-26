#!/usr/bin/env python3
"""Single switch for the Google review count shown across the site.

The count appears in visible text and in aria-labels, in both languages:
    "from 41 Google reviews"            (EN, all phrasings contain this)
    "aus 41 Google-Bewertungen"         (DE, all phrasings contain this)

Usage:
    python3 scripts/update_review_count.py 42        set the count everywhere
    python3 scripts/update_review_count.py --check   verify all pages agree

--check exits non-zero when pages disagree, so it can run in the QA chain.
"""
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

PATTERNS = [
    (re.compile(r"\b(\d+) Google reviews\b"), "{n} Google reviews"),
    (re.compile(r"\b(\d+) Google-Bewertungen\b"), "{n} Google-Bewertungen"),
]


def html_files():
    return sorted(p for p in ROOT_DIR.rglob("*.html"))


def scan():
    """Return {value: [files]} for every review count found on the site."""
    found = {}
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        for pattern, _ in PATTERNS:
            for value in pattern.findall(text):
                found.setdefault(int(value), set()).add(path.relative_to(ROOT_DIR))
    return found


def check():
    found = scan()
    if not found:
        print("No review counts found at all — selectors need updating.")
        return 1
    if len(found) == 1:
        value = next(iter(found))
        print(f"OK: every page says {value} Google reviews "
              f"({len(found[value])} files).")
        return 0
    print("MISMATCH — pages disagree on the review count:")
    for value, files in sorted(found.items()):
        print(f"  {value}: {len(files)} files")
        for f in sorted(files):
            print(f"      {f}")
    return 1


def set_count(n):
    changed = []
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        new_text = text
        for pattern, template in PATTERNS:
            new_text = pattern.sub(template.format(n=n), new_text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed.append(path.relative_to(ROOT_DIR))
    print(f"Set review count to {n} in {len(changed)} files:")
    for f in changed:
        print(f"  {f}")
    return 0


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    if sys.argv[1] == "--check":
        return check()
    if sys.argv[1].isdigit():
        return set_count(int(sys.argv[1]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
