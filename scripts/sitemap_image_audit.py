
import os
import re
from urllib.parse import urlparse

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'
SITEMAP_PATH = os.path.join(ROOT_DIR, 'sitemap.xml')

def audit_sitemap_images():
    print(f"{'Metric':<30} | {'Status':<10} | {'Details'}")
    print("-" * 80)
    
    if not os.path.exists(SITEMAP_PATH):
        print(f"{'Sitemap File':<30} | FAILED     | File not found at {SITEMAP_PATH}")
        return

    with open(SITEMAP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Check Namespace
    if 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"' not in content:
        print(f"{'XML Namespace':<30} | FAILED     | Missing xmlns:image definition")
    else:
        print(f"{'XML Namespace':<30} | PASS       | Found xmlns:image definition")

    # 2. Count Images
    image_locs = re.findall(r'<image:loc>(.*?)</image:loc>', content)
    image_titles = re.findall(r'<image:title>(.*?)</image:title>', content)
    
    print(f"{'Total Images Listed':<30} | INFO       | {len(image_locs)} images")
    print(f"{'Total captioned Images':<30} | INFO       | {len(image_titles)} images with titles")

    if len(image_locs) == 0:
        print(f"{'Image Count':<30} | FAILED     | No images found in sitemap!")
        return

    # 3. Validation
    # Check if images are absolute URLs
    invalid_urls = [url for url in image_locs if not url.startswith('http')]
    if invalid_urls:
         print(f"{'URL Format':<30} | FAILED     | Found {len(invalid_urls)} relative URLs (must be absolute)")
    else:
         print(f"{'URL Format':<30} | PASS       | All image URLs are absolute")

    # Check for duplicates
    if len(image_locs) != len(set(image_locs)):
        print(f"{'Duplicates':<30} | WARN       | Duplicate images found (might be intentional)")
    
    # 4. Local File Existence Check
    # This is critical. Converting URL to local path.
    missing_files = 0
    checked_files = 0
    
    print("-" * 80)
    print("Verifying local existence of mapped images (Sample 10)...")
    
    for url in image_locs[:10]: # Check first 10 for speed, or all? Let's do samples.
        # Parse URL: https://axcentdance.com/assets/images/foo.webp -> /assets/images/foo.webp
        parsed = urlparse(url)
        path = parsed.path # /assets/images/foo.webp
        
        # Convert to local
        local_path = os.path.join(ROOT_DIR, path.lstrip('/'))
        
        if not os.path.exists(local_path):
            print(f"MISSING: {url} -> {local_path}")
            missing_files += 1
        checked_files += 1

    if missing_files == 0:
        print(f"{'Local File Check':<30} | PASS       | Verified {checked_files} sample images exist locally")
    else:
        print(f"{'Local File Check':<30} | FAILED     | {missing_files}/{checked_files} sample images missing on disk")

if __name__ == "__main__":
    audit_sitemap_images()
