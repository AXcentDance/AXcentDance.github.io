"""Insert the header 'Login' link (More dropdown -> portal) into every page.

The master templates (index.html / de/index.html) already carry the link.
Every other page with the standard header gets it inserted right after the
etiquette entry of the "More" dropdown, reusing that entry's relative path
prefix so the link resolves correctly at any directory depth.

Idempotent: pages that already contain the Login entry are skipped.

Usage: python3 scripts/propagate_header_login.py
Verify afterwards with: python3 scripts/header_footer_checker.py
"""
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pages that intentionally do not carry the standard header (mirrors
# header_footer_checker.py) plus the portal pages themselves.
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

SKIP_DIRS = {".git", ".agent", ".claude", "System", "assets", "scripts", "tests", "supabase", "node_modules"}

ETIQUETTE_RE = re.compile(
    r'(?P<indent>[ \t]*)<a href="(?P<prefix>[^"]*?)etiquette"><span>[^<]*</span></a>'
)


def label_for(rel_path):
    return "Login"


def process(path, rel_path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if '"portal"><span>Login</span>' in content or re.search(r'href="[^"]*portal"><span>Login</span>', content):
        return "already"

    match = ETIQUETTE_RE.search(content)
    if not match:
        return "no-header"

    login_line = '%s<a href="%sportal"><span>%s</span></a>' % (
        match.group("indent"), match.group("prefix"), label_for(rel_path)
    )
    insertion = match.group(0) + "\n" + login_line
    content = content[:match.start()] + insertion + content[match.end():]

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "updated"


def main():
    updated, already, no_header = [], [], []
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            if not name.endswith(".html") or name in IGNORE_FILES:
                continue
            path = os.path.join(dirpath, name)
            rel_path = os.path.relpath(path, ROOT_DIR)
            result = process(path, rel_path)
            {"updated": updated, "already": already, "no-header": no_header}[result].append(rel_path)

    print("Updated: %d" % len(updated))
    for p in updated:
        print("  + %s" % p)
    print("Already had the link: %d" % len(already))
    if no_header:
        print("No standard dropdown found (skipped): %d" % len(no_header))
        for p in no_header:
            print("  - %s" % p)


if __name__ == "__main__":
    main()
