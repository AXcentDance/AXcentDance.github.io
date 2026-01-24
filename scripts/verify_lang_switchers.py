
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def check_switcher(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    rel_path = os.path.relpath(filepath, ROOT_DIR)
    is_german = rel_path.startswith('de/') or rel_path == 'de/index.html'

    # Pattern for switcher
    # We look for the anchor that says "DE" or "EN"
    # <a href="..." ...>DE</a>
    
    if is_german:
        # Look for EN link
        # <a href="..." ...>EN</a>
        # Regex: <a\s+href=["\']([^"\']+)["\'][^>]*>\s*EN\s*</a>
        match = re.search(r'<a\s+href=["\']([^"\']+)["\'][^>]*>\s*EN\s*</a>', content, re.IGNORECASE)
        target_lang = "EN"
    else:
        # Look for DE link
        match = re.search(r'<a\s+href=["\']([^"\']+)["\'][^>]*>\s*DE\s*</a>', content, re.IGNORECASE)
        target_lang = "DE"

    if not match:
        print(f"[MISSING] {rel_path}: Could not find {target_lang} switcher link.")
        return

    href = match.group(1)
    
    # Resolve href relative to filepath
    # If href is absolute? (http...) we check it loosely
    if href.startswith('http'):
        # Check if it looks right (contains /de/ or not)
        pass # Too complex to validate reachability without reqs, assume manual check if absolute
    else:
        # Resolve relative path
        dir_path = os.path.dirname(filepath)
        target_path = os.path.normpath(os.path.join(dir_path, href))
        
        if not os.path.exists(target_path):
            print(f"[BROKEN] {rel_path}: Switcher links to {href} (Resolved: {target_path}) -> FILE NOT FOUND")
        else:
            # print(f"[OK] {rel_path} -> {href}")
            pass

def main():
    print("Verifying visible Language Switchers...")
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'scripts' in dirs: dirs.remove('scripts')
        
        for file in files:
            if file.endswith('.html'):
                # Skip noindex pages? maybe not, they might still have switchers.
                # Skip components?
                check_switcher(os.path.join(root, file))

if __name__ == "__main__":
    main()
