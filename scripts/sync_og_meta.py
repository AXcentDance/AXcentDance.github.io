
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

def sync_og_tags():
    print("Syncing Open Graph Tags in /de/...")
    
    files_changed = 0
    
    de_files = []
    for root, dirs, files in os.walk(DE_DIR):
        for file in files:
            if file.endswith('.html'):
                de_files.append(os.path.join(root, file))
                
    for filepath in de_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # 1. Get Meta Description
        meta_desc_match = re.search(r'<meta name="description"\s+content="(.*?)"', content)
        if not meta_desc_match:
            print(f"[{os.path.basename(filepath)}] Skipping (No meta description found).")
            continue
            
        meta_desc = meta_desc_match.group(1)
        
        # 2. Fix or Add OG Description
        og_desc_match = re.search(r'<meta property="og:description"\s+content="(.*?)"', content)
        
        if og_desc_match:
            # Replace existing
            # We want to force it to match meta description for consistency in this pass
            # (unless we specifically want different ones, but usually parity is best for localized pages)
            
            # regex replace
            content = re.sub(
                r'<meta property="og:description"\s+content=".*?"',
                f'<meta property="og:description" content="{meta_desc}"',
                content
            )
        else:
            # Add it!
            # Find insertion point
            # Try to insert after og:title
            if re.search(r'<meta property="og:title"', content):
                content = re.sub(
                    r'(<meta property="og:title"[^>]*>)',
                    f'\\1\n    <meta property="og:description" content="{meta_desc}">',
                    content
                )
            # Or after og:type
            elif re.search(r'<meta property="og:type"', content):
                 content = re.sub(
                    r'(<meta property="og:type"[^>]*>)',
                    f'\\1\n    <meta property="og:description" content="{meta_desc}">',
                    content
                )
            # Or after description meta
            elif re.search(r'<meta name="description"', content):
                 content = re.sub(
                    r'(<meta name="description"[^>]*>)',
                    f'\\1\n    <meta property="og:description" content="{meta_desc}">',
                    content
                )


        # 3. Ensure OG Locale
        if '<meta property="og:locale" content="de_CH">' not in content:
             # Check if we have another locale?
             if '<meta property="og:locale"' in content:
                 # Replace
                 content = re.sub(r'<meta property="og:locale" content="[^"]+">', '<meta property="og:locale" content="de_CH">', content)
             else:
                 # Insert
                 # After description metadata?
                 content = content.replace(f'<meta name="description"\n    content="{meta_desc}">', f'<meta name="description"\n    content="{meta_desc}">\n  <meta property="og:locale" content="de_CH">')

        # 4. Ensure OG Title matches Title (Optional, but good for Cart/etc)
        # ... skipping for now to prioritize description matching ... 

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{os.path.basename(filepath)}] Synced OG Description/Locale.")
            files_changed += 1

    print(f"Finished. Updated {files_changed} files.")

if __name__ == "__main__":
    sync_og_tags()
