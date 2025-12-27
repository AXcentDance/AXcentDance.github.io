import os
import datetime

# Configuration
ROOT_URL = "https://axcentdance.com"
ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"
OUTPUT_FILE = os.path.join(ROOT_DIR, "sitemap.xml")

# Files to exclude from sitemap
EXCLUDED_FILES = [
    "404.html",
    "google", # google verification files
    "admin.html",
    "_login.html",
    "_signup.html",
    "thank-you.html",
    "thank-you-contact.html",
    "thank-you-trial.html",
    "portal.html", # Student portal usually behind login or private
]

def generate_sitemap():
    print("Generating sitemap.xml...")
    
    urls = []
    
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip system directories
        if ".git" in root or "node_modules" in root or "scripts" in root or "System" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            # Check exclusions
            should_exclude = False
            for exc in EXCLUDED_FILES:
                if exc in file:
                    should_exclude = True
                    break
            if should_exclude:
                continue
                
            filepath = os.path.join(root, file)
            
            # Get relative path
            rel_path = os.path.relpath(filepath, ROOT_DIR)
            
            # Convert to URL path
            # Remove index.html for root
            if rel_path == "index.html":
                url_path = "/"
            else:
                # Remove .html extension for clean URLs (if server supports it)
                # But typically sitemaps should match exact served URLs. 
                # If you use .html in links, put .html here. 
                # Based on the site's links (e.g. href="about"), it seems to rely on server config treating "about" as "about.html"
                # OR the links in footer are "guide-bachata" (no extension).
                # Let's check if the footer links have extensions. 
                # In index.html footer: href="guide-bachata" (no .html).
                # This suggests the server rewrites matching URLs or supports extensionless.
                # However, for the sitemap, it's safest to output what the server accepts.
                # If usage is extensionless, we should strip .html.
                clean_name = rel_path.replace(".html", "")
                url_path = f"/{clean_name}"
            
            # Get last modified time
            mtime = os.path.getmtime(filepath)
            lastmod = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
            # Priority
            if url_path == "/":
                priority = "1.0"
            elif "/" not in url_path.strip("/"): # Top level pages
                priority = "0.8"
            else:
                priority = "0.6"
                
            urls.append({
                "loc": f"{ROOT_URL}{url_path}",
                "lastmod": lastmod,
                "priority": priority
            })
            
    # Generate XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'
        
    xml_content += '</urlset>'
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)
        
    print(f"Sitemap generated with {len(urls)} URLs at {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_sitemap()
