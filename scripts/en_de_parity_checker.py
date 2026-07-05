import os
import re
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# EN-only pages with no DE counterpart expected
IGNORE_FILES = {
    "404.html",
    "admin.html",
    "_login.html",
    "_signup.html",
    "portal.html",
    "thank-you.html",
    "thank-you-contact.html",
    "thank-you-trial.html",
}


def profile(path):
    """Build a structural profile of a page: heading counts, schema types,
    canonical/hreflang presence. Language-independent by design."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return {
        "h1": len(re.findall(r"<h1[\s>]", content, re.IGNORECASE)),
        "h2": len(re.findall(r"<h2[\s>]", content, re.IGNORECASE)),
        "h3": len(re.findall(r"<h3[\s>]", content, re.IGNORECASE)),
        "schema_types": sorted(set(re.findall(r'"@type":\s*"([^"]+)"', content))),
        "canonical": len(re.findall(r'rel="canonical"', content)),
        "hreflang": len(re.findall(r'hreflang="', content)),
    }


def collect_pairs():
    pairs = []
    for d in ["", "blog-posts"]:
        abs_dir = os.path.join(ROOT_DIR, d)
        if not os.path.isdir(abs_dir):
            continue
        for name in sorted(os.listdir(abs_dir)):
            if not name.endswith(".html") or name in IGNORE_FILES:
                continue
            en_rel = os.path.join(d, name) if d else name
            de_rel = os.path.join("de", en_rel)
            pairs.append((en_rel, de_rel))
    return pairs


def check():
    print("## AXcent Dance: EN/DE Structural Parity Audit")
    print("Comparing heading counts, schema types, canonical and hreflang tags...")
    print("-" * 60)

    issues = 0
    for en_rel, de_rel in collect_pairs():
        de_path = os.path.join(ROOT_DIR, de_rel)
        if not os.path.isfile(de_path):
            print("[MISSING] %s has no DE counterpart (%s)" % (en_rel, de_rel))
            issues += 1
            continue
        en_prof = profile(os.path.join(ROOT_DIR, en_rel))
        de_prof = profile(de_path)
        for key in en_prof:
            if en_prof[key] != de_prof[key]:
                print("[DIVERGED] %s vs %s: %s differs (EN=%s, DE=%s)"
                      % (en_rel, de_rel, key, en_prof[key], de_prof[key]))
                issues += 1

    print("-" * 60)
    if issues:
        print("FAIL: %d EN/DE parity issues found." % issues)
    else:
        print("PASS: EN and DE versions are structurally in sync.")
    return issues


if __name__ == "__main__":
    sys.exit(1 if check() else 0)
