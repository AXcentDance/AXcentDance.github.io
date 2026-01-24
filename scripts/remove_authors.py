import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return

    new_content = content
    
    # Pattern 1: Entire div/span that only contains the author mention
    # <(div|span) class="post-meta"[^>]*>\s*(Written|Geschrieben)\s+(by|von)\s+<a[^>]*>Ale\s*&\s*Xidan</a>\s*</(div|span)>
    p1 = r'<(div|span)\s+class="post-meta"[^>]*>\s*(Written|Geschrieben)\s+(by|von)\s+<a[^>]*>Ale\s*&\s*Xidan</a>\s*</\1>'
    new_content = re.sub(p1, '', new_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Pattern 2: Mention with a preceding separator (bullet, etc.)
    # \s*[•|·|·]\s*(Written|Geschrieben)\s+(by|von)\s+<a[^>]*>Ale\s*&\s*Xidan</a>
    p2 = r'\s*[•|·|·]\s*(Written|Geschrieben)\s+(by|von)\s+<a[^>]*>Ale\s*&\s*Xidan</a>'
    new_content = re.sub(p2, '', new_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Pattern 3: Mention with a trailing separator
    p3 = r'(Written|Geschrieben)\s+(by|von)\s+<a[^>]*>Ale\s*&\s*Xidan</a>\s*[•|·|·]\s*'
    new_content = re.sub(p3, '', new_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Pattern 4: Bare mention
    p4 = r'(Written|Geschrieben)\s+(by|von)\s+<a[^>]*>Ale\s*&\s*Xidan</a>'
    new_content = re.sub(p4, '', new_content, flags=re.DOTALL | re.IGNORECASE)

    if new_content != content:
        print(f"Cleaned: {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root: continue
        for file in files:
            if file.endswith(".html"):
                clean_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
