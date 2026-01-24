
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def get_logo_link(filepath):
    """
    Returns the correct relative path to index.html for the logo.
    """
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    
    # If file is index.html, link is index.html
    if rel_path == 'index.html':
        return 'index.html'

    # If file is in root (e.g. about.html), link is index.html
    depth = rel_path.count(os.sep)
    if depth == 0:
        return 'index.html'
    
    # If depth > 0, link is ../ * depth + index.html
    return ("../" * depth) + "index.html"

def fix_header_logo(filepath):
    # Only process English pages (exclude /de/)
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    if rel_path.startswith('de' + os.sep) or rel_path == 'de':
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the logo link
    # <a href="..." class="logo">
    # or <a href="..." class="logo header-logo">
    # We want to capture the href value.
    
    # We look for <a href="[^"]*" class="logo
    # and replace the href with correct one.
    
    correct_link = get_logo_link(filepath)
    
    # Pattern: <a href="ANYTHING" class="logo
    # validation: must involve class="logo"
    
    logo_pattern = re.compile(r'(<a\s+href=")([^"]*)("\s+class="logo)')
    
    # We need to be careful not to match footer logo if it has class="logo footer-logo"
    # But usually footer logo has class="logo footer-logo".
    # Header logo usually has class="logo".
    # However, if order is swapped: class="logo" href="..."
    
    # Let's target the exact string from the user's issue if possible, or use a robust regex.
    # User said: "top left logo in the header"
    # In index.html: <a href="index.html" class="logo">
    # In blog-posts: <a href="../" class="logo">
    
    new_content = logo_pattern.sub(f'\\1{correct_link}\\3', content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed header logo in: {filepath}")

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'de' in dirs:
            dirs.remove('de')
            
        for file in files:
            if file.endswith(".html"):
                fix_header_logo(os.path.join(root, file))

if __name__ == "__main__":
    main()
