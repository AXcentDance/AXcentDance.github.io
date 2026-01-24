
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

DOMAIN = "https://axcentdance.com"

def get_corresponding_path(filename, lang):
    """
    Returns the absolute URL for a given filename and language version.
    """
    # Normalize filename (remove path)
    base = os.path.basename(filename)
    
    if lang == 'en':
        if base == 'index.html':
            return f"{DOMAIN}/"
        # Check if it needs Clean URL (optional, but good for cleanliness)
        clean = base.replace('.html', '')
        return f"{DOMAIN}/{clean}"
        
    elif lang == 'de':
        if base == 'index.html':
            return f"{DOMAIN}/de/"
        clean = base.replace('.html', '')
        return f"{DOMAIN}/de/{clean}"
    
    return None

def inject_hreflangs():
    print("Starting Hreflang Injection...")
    
    # 1. Map all available pages (EN and DE)
    # We want to know if a page exists in both languages.
    # If it exists in both, we inject the block.
    # If it exists only in one, we MIGHT still inject it pointing to itself? 
    # No, typically you only inject if there is a translation OR you want to be self-referencing.
    # Google recommends self-referencing canonical + hreflang. 
    # So we ALWAYS inject the block, but if the other language is missing, what do we do?
    # We simply omit the missing language? Or better:
    # The requirement is that *if* translation exists, link it.
    
    en_files = {f for f in os.listdir(ROOT_DIR) if f.endswith('.html')}
    de_files = {f for f in os.listdir(DE_DIR) if f.endswith('.html')}
    
    # Union of all logical pages (by basename)
    all_pages = en_files.union(de_files)
    
    files_changed = 0
    
    for page in all_pages:
        # Determine existence
        has_en = page in en_files
        has_de = page in de_files
        
        # Build the Hreflang Block
        tags = []
        
        # 1. EN Link
        if has_en:
            url_en = get_corresponding_path(page, 'en')
            tags.append(f'<link rel="alternate" hreflang="en" href="{url_en}" />')
            # x-default is usually EN for this site
            tags.append(f'<link rel="alternate" hreflang="x-default" href="{url_en}" />')
            
        # 2. DE Link
        if has_de:
            url_de = get_corresponding_path(page, 'de')
            tags.append(f'<link rel="alternate" hreflang="de" href="{url_de}" />')
            
        # If we don't have at least self-reference + translation, is it worth it?
        # Yes, self-reference is good practice properly with Canonical.
        # But specifically we want the pair.
        
        block = "\n  ".join(tags)
        
        # Process EN file
        if has_en:
            path = os.path.join(ROOT_DIR, page)
            process_file(path, block)
            files_changed += 1
            
        # Process DE file
        if has_de:
            path = os.path.join(DE_DIR, page)
            process_file(path, block)
            files_changed += 1

    print(f"Finished. Updated {files_changed} files.")

def process_file(filepath, new_block):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strategy: Replace existing Hreflang tags OR insert before </head> or canonical
    
    # 1. Remove existing Hreflang tags (any variation)
    # Be careful not to delete other links
    # Regex: <link rel="alternate" hreflang=...>
    
    content_clean = re.sub(r'\s*<link rel="alternate" hreflang="[^"]+" href="[^"]+" />', '', content)
    
    # 2. Insert New Block
    # Ideally after <link rel="canonical" ...>
    if '<link rel="canonical"' in content_clean:
         # Find the end of that line
         pattern = r'(<link rel="canonical" href="[^"]+">)'
         replacement = r'\1\n  ' + new_block
         new_content = re.sub(pattern, replacement, content_clean)
    else:
        # Insert before </head>
        new_content = content_clean.replace('</head>', f'{new_block}\n</head>')
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        # print(f"Updated {os.path.basename(filepath)}")

if __name__ == "__main__":
    inject_hreflangs()
