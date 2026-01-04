import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def check_image_seo():
    print(f"{'File':<40} | {'Issue':<40} | {'Details'}")
    print("-" * 120)
    
    issues_count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, ROOT_DIR)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find img tags
            img_tags = re.findall(r'<img\s+([^>]+)>', content, re.IGNORECASE)
            
            for attrs in img_tags:
                # Check for Alt
                alt_match = re.search(r'alt=["\'](.*?)["\']', attrs, re.IGNORECASE)
                src_match = re.search(r'src=["\'](.*?)["\']', attrs, re.IGNORECASE)
                
                src = src_match.group(1) if src_match else "UNKNOWN_SRC"
                
                # Ignore Facebook Pixel
                if "facebook.com/tr" in src:
                    continue
                
                # Check 1: Missing or empty alt
                if not alt_match:
                    print(f"{rel_path:<40} | Missing Alt Text              | Src: {src if src else 'UNKNOWN_SRC'}")
                    issues_count += 1
                elif not alt_match.group(1).strip():
                    # Empty alt is fine for decorative images if explicitly intended, but often an oversight.
                    # We'll warn about it.
                    print(f"{rel_path:<40} | Empty Alt Text                | Src: {src if src else 'UNKNOWN_SRC'}")
                    issues_count += 1
                    
                # Skip if empty src
                if not src:
                    print(f"{rel_path:<40} | Empty Src                     | Image tag has no source")
                    issues_count += 1
                    continue
                    
                # Check for legacy formats (not webp/svg)
                # Handle query params e.g. .webp?v=1
                src_clean = src.split('?')[0].lower()
                
                # Check for .webp extension OR /webp (for dynamic placeholders like placehold.co/../webp)
                if not src_clean.endswith('.webp') and not src_clean.endswith('/webp') and not src_clean.endswith('.svg') and not src.startswith('data:'):
                    print(f"{rel_path:<40} | Legacy Format (Not WebP)      | Src: {src}")
                    issues_count += 1

    print("-" * 120)
    print(f"Total potential SEO improvements found: {issues_count}")

if __name__ == "__main__":
    check_image_seo()
