import os
import re
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pages that intentionally do not carry the standard header/footer
IGNORE_FILES = {
    "404.html",
    "admin.html",
    "_admin.html",
    "_attendance.html",
    "_login.html",
    "_signup.html",
    "_videos.html",
    "portal.html",
    "thank-you.html",
    "thank-you-contact.html",
    "thank-you-trial.html",
    "new-afro-dance-classes-september.html",  # retired post, noindex redirect stub
}

MASTERS = {
    "en": "index.html",
    "de": os.path.join("de", "index.html"),
}


def extract_block(content, tag):
    """Extract the first top-level <tag>...</tag> block."""
    match = re.search(r"<%s[\s>].*?</%s>" % (tag, tag), content, re.DOTALL | re.IGNORECASE)
    return match.group(0) if match else None


def normalize(block):
    """Normalize a header/footer block so that only structural differences remain.

    Link paths (href/src) legitimately differ across directory depths, so
    attribute values for href/src/srcset are stripped. Whitespace is collapsed.
    """
    if block is None:
        return None
    block = re.sub(r'\s(href|src|srcset|action)="[^"]*"', r' \1=""', block)
    block = re.sub(r"<!--.*?-->", "", block, flags=re.DOTALL)
    block = re.sub(r"\s+", " ", block).strip()
    return block


def collect_pages(lang):
    pages = []
    if lang == "en":
        dirs = ["", "blog"]
    else:
        dirs = ["de", os.path.join("de", "blog")]
    for d in dirs:
        abs_dir = os.path.join(ROOT_DIR, d)
        if not os.path.isdir(abs_dir):
            continue
        for name in sorted(os.listdir(abs_dir)):
            if not name.endswith(".html") or name in IGNORE_FILES:
                continue
            rel = os.path.join(d, name) if d else name
            if rel in MASTERS.values():
                continue
            pages.append(rel)
    return pages


def check():
    print("## AXcent Dance: Header/Footer Consistency Audit")
    print("Comparing every page against the master template (index.html / de/index.html)...")
    print("-" * 60)

    mismatches = 0
    for lang, master_rel in MASTERS.items():
        master_path = os.path.join(ROOT_DIR, master_rel)
        with open(master_path, "r", encoding="utf-8") as f:
            master_content = f.read()
        master_blocks = {
            tag: normalize(extract_block(master_content, tag))
            for tag in ("header", "footer")
        }

        for rel in collect_pages(lang):
            with open(os.path.join(ROOT_DIR, rel), "r", encoding="utf-8") as f:
                content = f.read()
            for tag in ("header", "footer"):
                page_block = normalize(extract_block(content, tag))
                if page_block is None:
                    print("[MISSING] %s: no <%s> found" % (rel, tag))
                    mismatches += 1
                elif page_block != master_blocks[tag]:
                    print("[MISMATCH] %s: <%s> differs from %s" % (rel, tag, master_rel))
                    mismatches += 1

    print("-" * 60)
    if mismatches:
        print("FAIL: %d header/footer inconsistencies found." % mismatches)
    else:
        print("PASS: all headers and footers match their master template.")
    return mismatches


if __name__ == "__main__":
    sys.exit(1 if check() else 0)
