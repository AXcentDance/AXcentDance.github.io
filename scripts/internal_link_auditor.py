import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# Configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IGNORE_DIRS = ['node_modules', '.git', 'tmp', '.gemini', 'assets', 'scripts', 'System']

def get_all_html_files():
    html_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def extract_keywords_from_path(file_path):
    # Extract keywords from the filename/slug
    filename = os.path.basename(file_path).replace('.html', '')
    # Replace hyphens with spaces
    keywords = filename.replace('-', ' ')
    # Split into interesting chunks
    chunks = [keywords]
    if 'Milano' in keywords:
        chunks.append('Milano Sensual Congress')
    if 'Spring' in keywords:
        chunks.append('Spring Edition')
    return chunks

def audit_internal_links(new_file_path):
    new_file_rel = os.path.relpath(new_file_path, ROOT_DIR)
    new_file_slug = new_file_rel.replace('.html', '').replace('\\', '/')
    
    # Simple logic: avoid .html in comparison if our URLs are clean
    clean_target_url = new_file_slug
    if clean_target_url.startswith('de/'):
        is_german = True
        keywords = extract_keywords_from_path(new_file_path)
    else:
        is_german = False
        keywords = extract_keywords_from_path(new_file_path)

    print(f"\n--- Internal Link Audit for: {new_file_rel} ---")
    print(f"Target Keywords: {', '.join(keywords)}")
    
    all_files = get_all_html_files()
    suggestions = []

    for file_path in all_files:
        if file_path == new_file_path:
            continue
            
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        
        # Check language parity
        in_de = rel_path.startswith('de/')
        if is_german != in_de:
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for keywords in body text (ignoring nav/footer)
        main_content = soup.find('main') or soup.body
        if not main_content:
            continue
            
        text_content = main_content.get_text()
        
        # Check if keywords exist in text but link doesn't exist to this target
        found_keywords = [k for k in keywords if re.search(r'\b' + re.escape(k) + r'\b', text_content, re.IGNORECASE)]
        
        if found_keywords:
            # Check if there is already a link to the slug
            existing_links = [a['href'] for a in soup.find_all('a', href=True)]
            # Match variations: slug, slug.html, /slug, etc.
            link_exists = False
            for link in existing_links:
                # Handle relative links if in subdirectory
                abs_link_path = os.path.normpath(os.path.join(os.path.dirname(rel_path), link.replace('.html', '')))
                if abs_link_path.replace('\\', '/') == clean_target_url:
                    link_exists = True
                    break
            
            if not link_exists:
                suggestions.append({
                    'file': rel_path,
                    'found': found_keywords[0]
                })

    if suggestions:
        print("\n[SUGGESTIONS FOUND]")
        for s in suggestions:
            print(f" - Page: {s['file']}")
            print(f"   Context: Mentioned '{s['found']}' but no link found to {clean_target_url}")
            print(f"   Action: Consider weaving an internal link into the copy.")
    else:
        print("\n[PASS] No missing internal link opportunities found for major keywords.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_file = os.path.join(ROOT_DIR, sys.argv[1])
        if os.path.exists(target_file):
            audit_internal_links(target_file)
        else:
            print(f"Error: File {sys.argv[1]} not found.")
    else:
        print("Usage: python3 scripts/internal_link_auditor.py <path_to_new_file_relative_to_root>")
