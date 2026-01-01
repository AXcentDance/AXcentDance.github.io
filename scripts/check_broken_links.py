import os
import re
from urllib.parse import unquote

def check_broken_links(root_dir):
    print("Checking for broken local links and images...")
    print("-" * 60)
    
    issues_found = 0
    
    # Regex for finding links and images
    # 1. src="path"
    # 2. href="path" (ignoring external http/https/mailto/tel)
    # 3. url('path') or url("path")
    
    # We want to capture the path.
    # We ignore external links (starting with http, https, mailto, tel, #)
    
    link_patterns = [
        r'src=["\'](.*?)["\']',
        r'href=["\'](.*?)["\']',
        r'url\(["\']?(.*?)["\']?\)'
    ]
    
    for root, dirs, files in os.walk(root_dir):
        if 'node_modules' in root or '.git' in root or '_site' in root:
            continue
            
        for file in files:
            if file.endswith(".html") or file.endswith(".css"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for pattern in link_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            link = match.group(1).strip()
                            
                            # Skip empty links, fragments, or template variables
                            if not link or link.startswith('#') or link.startswith('{'):
                                continue
                                
                            # Skip external links
                            if link.startswith('http') or link.startswith('//') or link.startswith('mailto:') or link.startswith('tel:') or link.startswith('data:'):
                                continue

                            # Normalize link (remove query params)
                            clean_link = link.split('?')[0].split('#')[0]
                            
                            # Resolve absolute paths (from root) vs relative paths
                            if clean_link.startswith('/'):
                                # Relative to web root (root_dir)
                                target_path = os.path.join(root_dir, clean_link.lstrip('/'))
                            else:
                                # Relative to current file
                                target_path = os.path.join(root, clean_link)
                            
                            target_path = unquote(target_path)

                            # Check if file exists
                            if not os.path.exists(target_path) and not os.path.isdir(target_path):
                                # Double check if it's a directory (often linked without trailing slash)
                                if os.path.exists(target_path + '.html'):
                                    continue # Implicit .html extension
                                    
                                print(f"[MISSING] {rel_path} -> {link}")
                                issues_found += 1

                except Exception as e:
                    print(f"[ERROR] Could not read {rel_path}: {e}")

    if issues_found == 0:
        print("\n✅ No broken local links found!")
    else:
        print(f"\n❌ Found {issues_found} potential broken links.")

if __name__ == "__main__":
    root = os.getcwd()
    check_broken_links(root)
