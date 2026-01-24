
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

def localize_schema_urls():
    print("Starting Deep Schema URL Localization...")
    
    de_files = []
    for root, dirs, files in os.walk(DE_DIR):
        for file in files:
            if file.endswith('.html'):
                de_files.append(os.path.join(root, file))
    
    files_changed = 0
    
    for filepath in de_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # 1. FIX META OG:URL
        # <meta property="og:url" content="https://axcentdance.com/foo">
        # Should be https://axcentdance.com/de/foo (if not already)
        
        def og_replacer(match):
            url = match.group(1)
            # If it already has /de/, skip
            if "/de/" in url:
                return match.group(0)
            
            # If it matches root domain exactly?
            if url == "https://axcentdance.com/":
                 return '<meta property="og:url" content="https://axcentdance.com/de/">'
                 
            # Insert /de/
            new_url = url.replace("https://axcentdance.com/", "https://axcentdance.com/de/")
            return f'<meta property="og:url" content="{new_url}">'

        content = re.sub(r'<meta property="og:url" content="(https://axcentdance\.com/[^"]*)"', og_replacer, content)

        # 2. FIX JSON-LD URLs (Generic)
        # Target: "url": "https://axcentdance.com/...", "@id": "...", "sameAs" (careful), "mainEntityOfPage": "..."
        # We need to be careful NOT to break external links or assets.
        
        # Safe fields to localize:
        # - "url" (if internal page)
        # - "@id" (if internal page)
        # - "mainEntityOfPage" (if internal page)
        # - "item" (already done, but good to reinforce)
        
        # Asset URLs (images, logos) should probably STAY as root assets?
        # "https://axcentdance.com/assets/..." -> OK to keep english root if assets are not duplicated.
        # Check: do we have de/assets? No, mostly ../assets. 
        # So "https://axcentdance.com/assets/..." is correct and should NOT be localized to /de/assets unless that exists.
        
        def json_url_replacer(match):
            key = match.group(1) # "url" or "@id"
            url = match.group(2)
            
            # SKIP ASSETS
            if "/assets/" in url:
                return match.group(0)
                
            # SKIP ALREADY LOCALIZED
            if "/de/" in url:
                return match.group(0)

            # SKIP EXTERNAL (implicit by regex matching axcentdance.com)
            
            # SKIP HASH ONLY ? 
            if url == "https://axcentdance.com/#organization":
                return match.group(0) # Keep global ID? Or localize ID? Probably keep global ID for same business entity.
            
            # LINK TO ABOUT.HTML -> /de/about.html
            replacement = url.replace("https://axcentdance.com/", "https://axcentdance.com/de/")
            
            return f'{key}: "{replacement}"'

        # Regex: ("url"|"@id"|"mainEntityOfPage"|"item"): "(https://axcentdance.com/[^"]+)"
        # Note: key includes quote and spaces
        
        pattern = r'("url"|"@id"|"mainEntityOfPage"|"item")\s*:\s*"(https://axcentdance\.com/[^"]+)"'
        content = re.sub(pattern, json_url_replacer, content)
        
        # 3. FIX "author" URL or "publisher" URL
        # often points to about.html
        # The regex above likely catches them because key is "url" inside author object.
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{os.path.basename(filepath)}] Localized metadata URLs.")
            files_changed += 1

    print(f"Finished. Updated {files_changed} files.")

if __name__ == "__main__":
    localize_schema_urls()
