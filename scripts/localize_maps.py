
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

def localize_maps():
    print("Localizing Google Maps Links in /de/...")
    
    files_changed = 0
    
    for root, dirs, files in os.walk(DE_DIR):
        for file in files:
            if not file.endswith('.html'):
                continue
                
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 1. Embeds (iframe src)
            # src="https://www.google.com/maps/embed?pb=..."
            # Check if hl=de exists. If not, append it.
            # Regex for embed URLs
            
            def embed_replacer(match):
                url = match.group(1)
                if "hl=de" in url:
                    return match.group(0)
                
                # Append parameter
                if "?" in url:
                    new_url = url + "&hl=de"
                else:
                    new_url = url + "?hl=de"
                    
                return f'src="{new_url}"'

            content = re.sub(r'src="(https://www\.google\.com/maps/embed[^"]*)"', embed_replacer, content)
            
            # 2. External Links (a href)
            # https://www.google.com/maps/search/?api=1&query=...
            # https://maps.google.com/...
            # https://goo.gl/maps/... (shortlinks often don't take params well, but let's try or skip)
            # Generally adding hl=de works for search/dir links.
            
            def link_replacer(match):
                url = match.group(1)
                
                # Skip if already localized
                if "hl=de" in url:
                    return match.group(0)
                
                # Skip shortlinks if risk of breaking? 
                # maps.app.goo.gl usually redirects. Params might get lost but worth a try?
                # Actually, adding params to shortened URLs often breaks them.
                # Let's focus on google.com/maps links.
                
                if "maps.app.goo.gl" in url:
                    return match.group(0) # Skip shortlinks for safety unless we expand them
                    
                if "?" in url:
                    new_url = url + "&hl=de"
                else:
                    new_url = url + "?hl=de"
                    
                return f'href="{new_url}"'

            content = re.sub(r'href="(https://(?:www\.)?google\.com/maps[^"]*)"', link_replacer, content)
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[{file}] Added hl=de to Map links.")
                files_changed += 1

    print(f"Finished. Updated {files_changed} files.")

if __name__ == "__main__":
    localize_maps()
