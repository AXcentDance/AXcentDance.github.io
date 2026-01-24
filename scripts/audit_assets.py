
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

def audit_assets():
    print("## 2. Asset Integrity Audit")
    print("Checking for broken images/videos in /de/ pages due to path issues...")
    
    issues = []
    
    de_files = [f for f in os.listdir(DE_DIR) if f.endswith('.html')]
    
    for filename in de_files:
        path = os.path.join(DE_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex for src="..."
        # We look for relative paths that might be broken
        # Typical break: headers is copied but path is relative "assets/..." instead of "../assets/..."
        
        src_matches = re.finditer(r'src=["\']([^"\']+)["\']', content)
        
        for match in src_matches:
            src = match.group(1)
            
            # Skip absolute URLs (http, https, //)
            if src.startswith('http') or src.startswith('//') or src.startswith('data:'):
                continue
                
            # Skip root absolute paths (/) - assumes server mapped correctly
            # But let's verify file existence for strictness if possible.
            # actually we can verify local files.
            
            check_path = None
            if src.startswith('/'):
                check_path = os.path.join(ROOT_DIR, src.lstrip('/'))
            else:
                # Relative path
                check_path = os.path.join(DE_DIR, src)
            
            # Remove query params
            check_path = check_path.split('?')[0]
            check_path = check_path.split('#')[0]
            
            if not os.path.exists(check_path):
                # Common false positives: blobs constructed by JS?
                issues.append(f"[{filename}] Broken Asset: {src}")
                
        # Check CSS url(...)
        css_matches = re.finditer(r'url\([\"\']?([^)\"\']+)[\"\']?\)', content)
        for match in css_matches:
            url = match.group(1)
             # Skip absolute
            if url.startswith('http') or url.startswith('//') or url.startswith('data:'):
                continue
                
            check_path = None
            if url.startswith('/'):
                 check_path = os.path.join(ROOT_DIR, url.lstrip('/'))
            else:
                 check_path = os.path.join(DE_DIR, url)
                 
            # Remove query params
            check_path = check_path.split('?')[0]
            
            if not os.path.exists(check_path):
                 issues.append(f"[{filename}] Broken CSS Asset: {url}")

    if issues:
        print(f"⚠️ Found {len(issues)} broken assets:")
        for i in issues:
            print(i)
    else:
        print("✅ All assets in /de/ link correctly.")

if __name__ == "__main__":
    audit_assets()
