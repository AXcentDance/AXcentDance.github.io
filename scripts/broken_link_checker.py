import os
import re
from urllib.parse import unquote

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_broken_links():
    print("Checking for broken internal links...")
    print("-" * 60)
    

    # First, gather all existing files to validate against
    all_files = set()
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            path = os.path.join(root, file)
            all_files.add(path)
            

    issues_found = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            source_path = os.path.join(root, file)
            
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all hrefs
            # Matches href="value" or href='value'
            links = re.findall(r'href=["\'](.*?)["\']', content)
            
            for link in links:
                # Skip external links, anchors only, mailto, tel
                if link.startswith("http") or link.startswith("mailto:") or link.startswith("tel:") or link.startswith("#"):
                    continue

                # Skip common static assets we know exist or don't want to check rigorously here
                if link.endswith(".css") or link.endswith(".png") or link.endswith(".jpg") or link.endswith(".webp") or link.endswith(".ico") or link.endswith(".js"):
                    continue
                    
                # Clean link (remove hash for file check)
                link_path = link.split('#')[0]
                
                # Retrieve query params like style.css?v=2.2
                link_path = link_path.split('?')[0]  
                
                if not link_path:
                    # just #anchor
                    continue
                    
                # Resolve paths
                # If starts with /, it's relative to root
                if link_path.startswith("/"):
                    target_path = os.path.join(ROOT_DIR, link_path.lstrip("/"))
                else:
                    target_path = os.path.join(root, link_path)
                
                # Check for extensionless links (very common in this site)
                if not target_path.endswith(".html") and not os.path.isdir(target_path):
                     # If it doesn't have an extension, assume .html
                    if "." not in os.path.basename(target_path):
                        target_path_html = target_path + ".html"
                    else:
                        target_path_html = target_path
                else:
                    target_path_html = target_path
                    
                # Normalize
                target_path_html = os.path.normpath(target_path_html)
                
                # Verify existence

                if target_path_html not in all_files and not os.path.exists(target_path_html):
                    # One last check: might be a directory with index.html
                    if os.path.isdir(target_path):
                        if os.path.exists(os.path.join(target_path, "index.html")):
                            continue
                            
                    print(f"[BROKEN] In {file}: link to '{link}'")
                    issues_found += 1

    if issues_found == 0:
        print("Success! No broken internal links found.")
    else:
        print(f"\nFound {issues_found} broken links.")

if __name__ == "__main__":
    check_broken_links()
