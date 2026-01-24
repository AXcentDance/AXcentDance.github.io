
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def fix_links(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix _login -> _login.html
    # We look for href="_login" or href="../_login" etc.
    # We want to replace it with .html appended, ONLY if it doesn't already have it.
    
    # Regex replacement is safer than string replace to avoid _login.html.html
    
    # Pattern: href=" (any valid path ending in _login) "
    # We capture the quote, the path, and the quote.
    
    # Replace href="_login" -> href="_login.html"
    content = re.sub(r'href="([^"]*/_login)"', r'href="\1.html"', content)
    content = re.sub(r"href='([^']*/_login)'", r"href='\1.html'", content)
    
    # Replace href="portal" -> href="portal.html"
    content = re.sub(r'href="([^"]*/portal)"', r'href="\1.html"', content)
    content = re.sub(r"href='([^']*/portal)'", r"href='\1.html'", content)

    # Specific cases for root-relative that might be just "portal" or "_login"
    # The regex above matches "path/ending/in/_login".
    # If it is just href="_login", the group 1 is "_login". Result is "_login.html". Correct.
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed links in: {filepath}")

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'scripts' in dirs:
            dirs.remove('scripts') # Skip scripts dir
            
        for file in files:
            if file.endswith(".html"):
                fix_links(os.path.join(root, file))

if __name__ == "__main__":
    main()
