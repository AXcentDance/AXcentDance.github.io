
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def audit_relative_links():
    print(f"Starting Relative Link Audit in {ROOT_DIR}...\n")
    
    broken_links = []
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'node_modules' in root or '.git' in root: 
            continue
            
        for file in files:
            if not file.endswith('.html'):
                continue
                
            source_path = os.path.join(root, file)
            # print(f"Checking {source_path}...")
            
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    
                for a in soup.find_all('a'):
                    href = a.get('href')
                    if not href:
                        continue
                        
                    # Skip externals, anchors, mailto, tel, javascript
                    if href.startswith(('http', '//', '#', 'mailto:', 'tel:', 'javascript:')):
                        continue
                        
                    # Handle in-page anchors with path e.g. "index.html#contact"
                    href_clean = href.split('#')[0]
                    if not href_clean: # Was just "#" or "#something"
                        continue
                        
                    # Resolve path
                    # source_dir = /Users/.../de/
                    # href = guide-bachata.html
                    # target = /Users/.../de/guide-bachata.html
                    
                    source_dir = os.path.dirname(source_path)
                    target_path = os.path.join(source_dir, href_clean)
                    
                    # Normalize (resolve ../)
                    target_path = os.path.normpath(target_path)
                    
                    if not os.path.exists(target_path) and not os.path.isdir(target_path):
                        # Special case: The user might be linking to a directory implying index.html?
                        # But mostly we want explicit .html
                        
                        relative_source = os.path.relpath(source_path, ROOT_DIR)
                        broken_links.append({
                            'source': relative_source,
                            'link': href,
                            'resolved_to': os.path.relpath(target_path, ROOT_DIR)
                        })
                        
            except Exception as e:
                print(f"Error parsing {source_path}: {e}")

    # Report
    if broken_links:
        print(f"FOUND {len(broken_links)} BROKEN INTERNAL LINKS:\n")
        # Group by source folder for easier reading?
        # Or just list
        for issue in broken_links:
            print(f"FILE: {issue['source']}")
            print(f"  LINK:   {issue['link']}")
            print(f"  MISSING: {issue['resolved_to']}")
            print("-" * 40)
    else:
        print("SUCCESS: No broken relative links found!")

if __name__ == "__main__":
    audit_relative_links()
