
import os
import re
from urllib.parse import urlparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

def get_canonical_url(content):
    match = re.search(r'<link rel="canonical" href="([^"]+)"', content)
    return match.group(1) if match else None

def get_hreflangs(content):
    # Returns dict: {'en': 'url', 'de': 'url', ...}
    matches = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', content)
    return {lang: url for lang, url in matches}

def audit_hreflang():
    print("## 1. Hreflang Reciprocity Audit")
    print("Verifying that every EN page points to DE, and DE points back to EN...")
    
    issues = []
    
    en_files = [f for f in os.listdir(ROOT_DIR) if f.endswith('.html') and f != '404.html']
    
    for en_file in en_files:
        path = os.path.join(ROOT_DIR, en_file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        hreflangs = get_hreflangs(content)
        
        # Check if it has DE link
        if 'de' not in hreflangs:
            issues.append(f"[EN] {en_file}: Missing hreflang='de'")
            continue
            
        de_url = hreflangs['de']
        
        # Handle Clean URLs:
        # https://axcentdance.com/de/foo -> file is foo.html
        # https://axcentdance.com/de/ -> file is index.html
        
        parsed = urlparse(de_url)
        de_path_rel = parsed.path.strip('/') # de/foo or de
        
        if de_path_rel == 'de' or de_path_rel == 'de/':
            de_filename = 'index.html'
        else:
            # remove 'de/' prefix
            name = de_path_rel.replace('de/', '')
            # add .html if missing
            if not name.endswith('.html'):
                name += '.html'
            de_filename = name
            
        de_file_path = os.path.join(DE_DIR, de_filename)
        
        if not os.path.exists(de_file_path):
             issues.append(f"[EN] {en_file}: Hreflang points to non-existent file {de_file_path} (URL: {de_url})")
             continue
             
        # Check reciprocity
        with open(de_file_path, 'r', encoding='utf-8') as f:
            de_content = f.read()
            
        de_hreflangs = get_hreflangs(de_content)
        
        if 'en' not in de_hreflangs:
             # Look closer: maybe it's x-default? No, typically explicit EN needed.
             issues.append(f"[DE] {de_filename}: Missing hreflang='en' (Broken Reciprocity for {en_file})")
             continue
             
    print(f"Scanned {len(en_files)} English files.")
    
    if issues:
        print(f"⚠️ Found {len(issues)} Hreflang issues:")
        for i in issues:
            print(i)
    else:
        print("✅ Hreflang Logic is perfectly reciprocal.")

if __name__ == "__main__":
    audit_hreflang()
