import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

# Mapping of specific German files to English URLs if they differ significantly, 
# otherwise we assume de/foo.html -> /foo
# We will check if /foo.html exists in ROOT.
SPECIAL_MAPPINGS = {
    'index.html': '/',
}

def fix_links_and_switcher():
    print("Starting German Link Fixer...")
    
    # Get all DE HTML files
    de_files = [f for f in os.listdir(DE_DIR) if f.endswith('.html')]
    
    # Get all EN HTML files for validation
    en_files = set(os.listdir(ROOT_DIR))
    
    for filename in de_files:
        filepath = os.path.join(DE_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # 1. FIX INTERNAL LINKS (../page.html -> page.html)
        # We look for href="../something" where something is NOT assets, style, script, favicon
        # And where 'something' exists in DE_DIR
        
        def link_replacer(match):
            full_ref = match.group(0) # href="../foo"
            quote = match.group(1)
            link_path = match.group(2) # foo
            
            # Skip assets
            if link_path.startswith('assets/') or link_path.startswith('style') or link_path.startswith('script') or link_path.startswith('manifest') or link_path.startswith('humans'):
                return full_ref
            
            # Remove anchor for file check
            clean_link = link_path.split('#')[0].split('?')[0]
            
            # Check if this file exists in DE_DIR
            # Case 1: .html extension
            if clean_link in de_files:
                # It exists in DE, so we should link to it directly (relative)
                return f'href={quote}{link_path}{quote}'
            
            # Case 2: No extension, but .html exists (e.g. href="../about" -> href="about" if about.html exists)
            if clean_link + ".html" in de_files:
                 return f'href={quote}{link_path}{quote}'
                 
            return full_ref

        # Regex for href="../..."
        # We need to capture the quote type
        content = re.sub(r'href=(["\'])\.\./([^"\']+)(["\'])', link_replacer, content)
        
        # 2. FIX LANGUAGE SWITCHER
        # Determine English slug
        if filename in SPECIAL_MAPPINGS:
            en_slug = SPECIAL_MAPPINGS[filename]
        else:
            # remove .html for the clean URL style used in the site
            en_slug = "/" + filename.replace('.html', '')
            
        # Regex to find the EN link in the switcher
        # Looking for <div class="lang-switch"> ... <a href="...">EN</a>
        
        # We'll use a broader replacements for the switcher block content to ensure it's correct
        # Strategy: Find the EN link specifically inside lang-switch or near it.
        # But simpler: The user wants "Add in all the header... the de/en switch"
        # We will look for the existing switch and update the href.
        
        # Pattern: <a href="[^"]*"[^>]*>EN</a>
        # We want to replace the href.
        
        # NOTE: This regex might be risky if there are other EN links, but "EN" text is specific to switcher usually.
        # Let's target the specific structure:
        # <a href="..." ...>EN</a>
        
        def switcher_replacer(match):
            # match.group(1): attributes before href
            # match.group(2): old href
            # match.group(3): attributes after href
            # match.group(4): style/content before EN
            return f'<a href="{en_slug}"{match.group(3)}'

        # More robust regex targeting the a tag containing EN
        # We look for <a href="..." style="...">EN</a>
        # We only replace the href.
        
        # Check if file has "EN" link
        if ">EN</a>" in content:
            # Replace href for EN link
            # We assume the structure: <a href="OLD_LINK" [styles]>EN</a>
            content = re.sub(r'<a href="([^"]+)"([^>]*)>EN</a>', f'<a href="{en_slug}"\\2>EN</a>', content)
            print(f"[{filename}] Updated Switcher -> {en_slug}")
            
        # 3. FIX Navbar links that might be absolute to root (e.g. href="/about") -> href="about"
        # The user said "every link to another page in the de version links to another de page"
        # If we have href="/about", it goes to EN.
        # We should change to "about" (relative -> DE)
        
        def abs_link_replacer(match):
            quote = match.group(1)
            link_path = match.group(2) # about
            
            # Skip empty or strict root
            if link_path == "" or link_path == "/":
                 return match.group(0) # Keep / for root (though strictly DE root is /de/)
                 
            # If it's a known DE file
            clean = link_path.split('#')[0]
            if clean + ".html" in de_files or clean in de_files:
                return f'href={quote}{link_path}{quote}'
                
            return match.group(0)

        # content = re.sub(r'href=(["\'])/([^"\']+)(["\'])', abs_link_replacer, content)
        # Actually, let's be careful with pure absolute links. 
        # The site seems to use relative links mostly. 
        # But I saw href="/about" in my manual check? No, I saw href="about".
        # I saw href="../bachata-beginner-2.html". That was the main issue.
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{filename}] Fixed links.")
        else:
            print(f"[{filename}] No changes.")

if __name__ == "__main__":
    fix_links_and_switcher()
