
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def remove_auth_links(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Remove Mobile Bottom Nav Item "Portal"
    # <a href="...portal..." class="nav-item"> ... </a>
    # CAUTION: Regex spanning multiple lines.
    # Pattern: <a href="[^"]*portal[^"]*" class="nav-item">.*?</a>
    # We use DOTALL.
    
    # Mobile Bottom Nav Item: Portal
    # <a href="../portal" class="nav-item">\s*<svg.*?</svg>\s*<span>Portal</span>\s*</a>
    
    content = re.sub(r'<a href="[^"]*portal[^"]*" class="nav-item">.*?</a>', '', content, flags=re.DOTALL)
    
    # 2. Remove Drawer Link "Log In" if present (usually commented out but let's check widely)
    # <a href="..._login..." class="drawer-link" ...> ... </a>
    content = re.sub(r'<a href="[^"]*_login[^"]*" class="drawer-link"[^>]*>.*?</a>', '', content, flags=re.DOTALL)
    
    # 3. Remove "Portal" from Desktop Nav if it exists (check index.html structure previously seen? No, index.html didn't show Portal in desktop nav)
    # But just in case:
    # <a href="...portal...">Portal</a>
    # Be careful not to match random text.
    
    # 4. Remove commented out links if user wants "all traces"
    content = re.sub(r'<!--\s*<a href="[^"]*_login[^"]*".*?-->', '', content, flags=re.DOTALL)

    
    # 5. Remove CSP "https://*.supabase.co" reference
    content = content.replace(' https://*.supabase.co', '')
    
    if content != original_content:
        # Cleanup empty lines created by removal?
        # Maybe not strictly necessary providing HTML valid.
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Cleaned auth links in: {filepath}")

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'scripts' in dirs:
            dirs.remove('scripts')
            
        for file in files:
            if file.endswith(".html"):
                remove_auth_links(os.path.join(root, file))

if __name__ == "__main__":
    main()
