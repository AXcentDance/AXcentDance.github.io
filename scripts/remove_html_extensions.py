import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # 1. Handle href attributes using the smart logic from before
    def replace_href(match):
        start_quote = match.group(1)
        url = match.group(2)
        end_quote = match.group(3)
        
        # If it's an absolute URL for our domain, we process it.
        # If it's relative, we process it.
        # If it's external (not axcentdance.com), we skip.
        
        is_absolute_internal = url.startswith('https://axcentdance.com/') or url.startswith('http://axcentdance.com/')
        is_external = (url.startswith('http://') or url.startswith('https://') or url.startswith('//')) and not is_absolute_internal
        
        if is_external or url.startswith('mailto:') or url.startswith('tel:') or url.startswith('#') or url.startswith('javascript:'):
            return match.group(0)

        # Handle valid relative or absolute-internal links containing .html
        if '.html' in url:
            base_path = url.split('?')[0].split('#')[0]
            suffix = url[len(base_path):]
            
            if base_path.endswith('.html'):
                # Handle index specifically
                if base_path.endswith('/index.html') or base_path == 'index.html':
                     # index.html -> ./ or /
                     # path/index.html -> path/
                     # https://site.com/index.html -> https://site.com/
                     
                     if base_path == 'index.html':
                         new_base = './'
                     else:
                         new_base = base_path[:-10] # remove index.html, leave trailing slash (or empty if it was just /index.html... wait /index.html is len 11, index.html is 10)
                         if base_path == '/index.html':
                             new_base = '/'
                         elif base_path.endswith('/index.html'):
                             new_base = base_path[:-10] # .../index.html -> .../
                else:
                    new_base = base_path[:-5] # remove .html
                
                new_url = new_base + suffix
                return f'href={start_quote}{new_url}{end_quote}'
        
        return match.group(0)

    content = re.sub(r'href=(["\'])(.*?)(["\'])', replace_href, content)

    # 2. Handle Absolute URLs in general (including content="...", "url": "..." in JSON-LD)
    # Target https://axcentdance.com/....html
    # We warn to be careful not to break assets if they were .html (unlikely for assets)
    
    def replace_absolute(match):
        url = match.group(0)
        # Check if it ends in .html or .html? or .html#
        # Regex capture ensures we match the whole URL
        
        if 'index.html' in url:
             if url.endswith('/index.html'):
                 return url[:-10]
             if url == 'https://axcentdance.com/index.html':
                 return 'https://axcentdance.com/'
        
        if url.endswith('.html'):
            return url[:-5]
            
        return url

    # Regex for absolute URLs appearing anywhere (like in json-ld or meta content)
    # We look for https://axcentdance.com/[something].html
    # Be careful with boundaries.
    content = re.sub(r'https://axcentdance\.com/[a-zA-Z0-9_\-/]+\.html', replace_absolute, content)

    if content != original_content:
        print(f"Updating {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    print("Starting Clean URLs processing (Phase 2: Absolute & cleanup)...")
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or ".agent" in root:
            continue
            
        for file in files:
            if file.endswith(".html"):
                process_file(os.path.join(root, file))
    print("Done.")

if __name__ == "__main__":
    main()
