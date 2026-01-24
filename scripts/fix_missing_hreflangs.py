
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

# List of files flagged by audit_hreflang.py
FILES_TO_FIX = [
    'thank-you.html',
    'thank-you-contact.html',
    'thank-you-trial.html'
    # We omit admin, portal, _login, _signup because they likely don't have DE versions yet
    # based on typical workflows. We will verify existence in the loop.
]

def get_canonical_link(filepath):
    # Construct standard canonical based on filename
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    # Remove .html for the URL if that's the convention, OR keep it.
    # The existing files seem to use .html in canonical? Or usually clean URLs.
    # Let's check a sample. about.html -> href=".../about" (Clean).
    
    clean_path = rel_path.replace('.html', '')
    if clean_path == 'index':
        clean_path = ''
        
    return f"https://axcentdance.com/{clean_path}"

def add_hreflang(filepath):
    # Check if DE version exists
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    de_path = os.path.join(ROOT_DIR, 'de', rel_path)
    
    if not os.path.exists(de_path):
        print(f"Skipping {filepath}: DE version not found.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if we already have hreflang (script check might be strict or we missed it)
    if 'hreflang="de"' in content:
        print(f"Skipping {filepath}: Hreflang already present.")
        return

    # Prepare tags
    # URL construction: https://axcentdance.com/filename (clean)
    # DE URL: https://axcentdance.com/de/filename
    
    basename = os.path.splitext(os.path.basename(filepath))[0]
    if basename == 'index':
        en_url = "https://axcentdance.com/"
        de_url = "https://axcentdance.com/de/"
    else:
        en_url = f"https://axcentdance.com/{basename}"
        de_url = f"https://axcentdance.com/de/{basename}"

    hreflang_block = f"""    <link rel="canonical" href="{en_url}">
    <link rel="alternate" hreflang="en" href="{en_url}" />
    <link rel="alternate" hreflang="de" href="{de_url}" />
    <link rel="alternate" hreflang="x-default" href="{en_url}" />"""

    # Insert before </head>, or better, after <meta charset...> or <title>
    # Let's look for <title>...</title> and insert after.
    
    match = re.search(r'</title>', content)
    if match:
        new_content = content[:match.end()] + '\n' + hreflang_block + content[match.end():]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Added hreflang to: {filepath}")
    else:
        print(f"Skipping {filepath}: No </title> found.")

def main():
    for filename in FILES_TO_FIX:
        filepath = os.path.join(ROOT_DIR, filename)
        if os.path.exists(filepath):
            add_hreflang(filepath)
        else:
            print(f"File not found: {filename}")

if __name__ == "__main__":
    main()
