
import os
import re
import datetime
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'
DOMAIN = 'https://axcentdance.com'

def is_noindex(filepath):
    """Checks if a file has <meta name="robots" content="noindex...">"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if re.search(r'<meta\s+name=["\']robots["\']\s+content=["\'].*?noindex.*?["\']', content, re.IGNORECASE):
        return True
    return False

def get_lastmod(filepath):
    """Returns file modification time in YYYY-MM-DD format."""
    timestamp = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def get_url_path(filepath):
    """Converts filesystem path to URL path."""
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    
    # Handle Windows backslashes if running there (not case here but good practice)
    rel_path = rel_path.replace(os.sep, '/')
    
    # Remove .html extension for clean URLs (assuming server handles it), 
    # OR keep it if that's the convention. 
    # Current sitemap has clean URLs (e.g. https://axcentdance.com/about)
    # So we strip .html, except for index.html which becomes /
    
    if rel_path.endswith('.html'):
        rel_path = rel_path[:-5]
        
    if rel_path == 'index':
        return '/'
    if rel_path == 'de/index':
        return '/de/'
    
    return '/' + rel_path

def get_page_images(filepath):
    """Extracts images from an HTML file for sitemap."""
    images = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        seen_src = set()
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
                
            # Skip external images, tracking pixels, or data URIs
            if src.startswith(('http', '//', 'data:', 'blob:')):
                continue
                
            # Convert relative path to absolute URL
            # Logic: If src is absolute path (starts with /), append to domain
            # If relative, resolve based on file directory (complex) 
            # BUT for this site, images are mostly in assets/
            
            # Simple handle for /assets
            if src.startswith('/'):
                img_url = DOMAIN + src
            else:
                # Resolve relative to current page location if possible
                # Or simplistic assumption: most used as relative from root?
                # Actually, standard is to map strictly.
                # Let's clean it up: remove ../ if present
                clean_src = src.replace('../', '').replace('./', '')
                if clean_src.startswith('assets/'):
                    img_url = f"{DOMAIN}/{clean_src}"
                else:
                    # Fallback for images in same dir
                    # But sitemap needs absolute
                   continue

            if img_url in seen_src:
                continue
                
            img_data = {
                'loc': img_url
            }
            
            # Add caption (alt) and title if available
            alt = img.get('alt')
            if alt:
                img_data['title'] = alt # Use alt as title/caption for sitemap
                
            images.append(img_data)
            seen_src.add(img_url)
            
    except Exception as e:
        print(f"Error parsing images for {filepath}: {e}")
        
    return images

def generate_sitemap():
    print("Generating sitemap.xml with images...")
    
    # 1. Walk and collect all indexable HTML files
    all_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'scripts' in dirs: dirs.remove('scripts')
        if '.git' in dirs: dirs.remove('.git')
        if 'assets' in dirs: dirs.remove('assets')
        
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                if not is_noindex(filepath):
                    all_files.append(filepath)

    # 2. Process pairs
    # We want to group EN and DE pages to generate hreflang entries
    
    # Map: 'rel_path_without_lang_prefix' -> { 'en': path, 'de': path }
    # e.g. 'about' -> { 'en': '.../about.html', 'de': '.../de/about.html' }
    
    page_map = {}
    
    for filepath in all_files:
        rel_path = os.path.relpath(filepath, ROOT_DIR)
        
        if rel_path.startswith('de/'):
            key = rel_path[3:] # Strip 'de/'
            lang = 'de'
        else:
            key = rel_path
            lang = 'en'
            
        if key not in page_map:
            page_map[key] = {}
        
        page_map[key][lang] = filepath

    # 3. Build XML entries
    xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n'
    # Add Image Namespace
    xml_output += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    
    # Iterate through map to build URL entries
    for key, variants in page_map.items():
        # Each variant gets its own <url> entry
        for lang, filepath in variants.items():
            url = DOMAIN + get_url_path(filepath)
            lastmod = get_lastmod(filepath)
            
            # Priority
            if key in ['index.html', 'de/index.html', 'index', 'de/index']:
                priority = '1.0'
            elif 'blog-posts' in key:
                priority = '0.6'
            else:
                priority = '0.8'
                
            xml_output += '  <url>\n'
            xml_output += f'    <loc>{url}</loc>\n'
            xml_output += f'    <lastmod>{lastmod}</lastmod>\n'
            xml_output += f'    <priority>{priority}</priority>\n'
            
            # Hreflang Alternates
            # Must list ALL variants (including self)
            if 'en' in variants:
                en_url = DOMAIN + get_url_path(variants['en'])
                xml_output += f'    <xhtml:link rel="alternate" hreflang="en" href="{en_url}" />\n'
                xml_output += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{en_url}" />\n'
            
            if 'de' in variants:
                de_url = DOMAIN + get_url_path(variants['de'])
                xml_output += f'    <xhtml:link rel="alternate" hreflang="de" href="{de_url}" />\n'
                
            # IMAGE SITEMAP ENTRIES
            page_images = get_page_images(filepath)
            for img in page_images:
                xml_output += '    <image:image>\n'
                xml_output += f'      <image:loc>{img["loc"]}</image:loc>\n'
                if 'title' in img:
                     # Escape XML characters
                    safe_title = img['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", "&apos;")
                    xml_output += f'      <image:title>{safe_title}</image:title>\n'
                xml_output += '    </image:image>\n'
                
            xml_output += '  </url>\n'

    xml_output += '</urlset>'
    
    with open(os.path.join(ROOT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(xml_output)
    
    print(f"Sitemap generated with {len(all_files)} URLs and comprehensive image definitions.")

if __name__ == "__main__":
    generate_sitemap()
