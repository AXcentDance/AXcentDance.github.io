import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def check_advanced_image_quality():
    print(f"{'File':<40} | {'Issue':<30} | {'Details'}")
    print("-" * 120)
    
    issues_count = 0
    total_files_checked = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root or "System" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            total_files_checked += 1
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, ROOT_DIR)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check 1: At least one picture per page
            # We check for <img> tags
            img_tags = re.findall(r'<img\s+([^>]+)>', content, re.IGNORECASE)
            
            # Skip check for specific utility files if needed (e.g., partials starting with _)
            
            # Exclusion list for "No Images" check (Utility/Legal/Error pages)
            # FAQ is explicitly KEPT in the check.
            IGNORED_NO_IMAGES = [
                '404.html', 'terms.html', 'imprint.html', 'privacy.html', 
                'admin.html', 'thank-you.html', 'thank-you-contact.html', 
                'thank-you-trial.html', 'portal.html', 'cart.html'
            ]
            
            if not img_tags and not file.startswith("_"):
                if file in IGNORED_NO_IMAGES:
                    continue # Skip checking these files entirely for image issues
                    
                # Also check if there are no background images in style blocks? No, user asked for "picture"
                print(f"{rel_path:<40} | No Images Found              | Page has 0 <img> tags")
                issues_count += 1
                continue # If no images, skip other checks for this file
            
            # Check 2 & 3: Individual Image Attributes
            for index, attrs in enumerate(img_tags):
                src_match = re.search(r'src=["\'](.*?)["\']', attrs, re.IGNORECASE)
                alt_match = re.search(r'alt=["\'](.*?)["\']', attrs, re.IGNORECASE)
                width_match = re.search(r'width=["\'](.*?)["\']', attrs, re.IGNORECASE)
                height_match = re.search(r'height=["\'](.*?)["\']', attrs, re.IGNORECASE)
                srcset_match = re.search(r'srcset=["\'](.*?)["\']', attrs, re.IGNORECASE)
                
                src = src_match.group(1) if src_match else "UNKNOWN"
                
                # Filter out SVGs or tracking pixels often used without dimensions
                if src.endswith(".svg"):
                    continue
                
                # Check 2: Alt Text
                if not alt_match or not alt_match.group(1).strip():
                    print(f"{rel_path:<40} | Missing/Empty Alt            | Src: {src[:30]}...")
                    issues_count += 1
                
                # Check 3: Dimensions (CLS Prevention)
                if not width_match or not height_match:
                    # Check if it's a "blob" or decorative element? User said "perfect dimensions"
                    print(f"{rel_path:<40} | Missing Width/Height         | Src: {src[:30]}...")
                    issues_count += 1
                
                # Check 4: Responsive Sizing (srcset or picture tag)
                
                is_responsive = False
                if srcset_match:
                    srcset_val = srcset_match.group(1)
                    # Check for 3 distinct sizes (comma separated) AND that they are WebP
                    # e.g. "a.webp 500w, b.webp 1000w, c.webp 1500w" matches 3
                    entries = [x for x in srcset_val.split(',') if x.strip()]
                    
                    # Filter for WebP
                    webp_entries = [x for x in entries if '.webp' in x.lower() or '/webp' in x.lower()]
                    
                    if len(webp_entries) >= 3:
                        is_responsive = True
                    else:
                        print(f"{rel_path:<40} | Weak Responsive (<3 WebP sizes)| Src: {src[:30]}...")
                        issues_count += 1
                        is_responsive = True # Handled, prevent falling into "No srcset" error

                
                if not is_responsive:
                     # Check if <picture> exists nearby? Hard. 
                     # Let's flag it if no srcset is found, as modern responsive images usually use it.
                     # Unless it's a small icon?
                     if "icon" not in src and "logo" not in src:
                        print(f"{rel_path:<40} | Non-Responsive (No srcset)   | Src: {src[:30]}...")
                        issues_count += 1

                # Check 5: Lazy Loading (Context Aware)
                loading_match = re.search(r'loading=["\'](.*?)["\']', attrs, re.IGNORECASE)
                is_lazy = loading_match and loading_match.group(1).lower() == 'lazy'
                
                if index < 2:
                    # Top of page (LCP candidates): Should NOT be lazy
                    if is_lazy:
                        print(f"{rel_path:<40} | LCP Image Lazy Loaded (Bad)| Src: {src[:30]}...")
                        issues_count += 1
                else:
                    # Below fold: MUST be lazy
                    if not is_lazy:
                         print(f"{rel_path:<40} | Missing Lazy Load            | Src: {src[:30]}...")
                         issues_count += 1

    print("-" * 120)
    print(f"Total files checked: {total_files_checked}")
    print(f"Total potential improvements found: {issues_count}")

if __name__ == "__main__":
    check_advanced_image_quality()
