import os
import re

# Blog posts to refactor
TARGET_FILES = [
    "blog-posts/blog-new-location.html",
    "blog-posts/christmas-break-2025.html",
    "blog-posts/connection-101.html",
    "blog-posts/dance-tips-1-frame.html",
    "blog-posts/romeo-prince-collaboration-2025.html",
    "blog-posts/roots-of-bachata.html",
    "blog-posts/what-to-wear-bachata.html"
]

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def refactor_blog_post(filename):
    filepath = os.path.join(ROOT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename} (Not found)")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract Page Title for Alt Text
    title_match = re.search(r'<title>(.*?)(\| AXcent Dance)?</title>', content, re.IGNORECASE)
    page_title = title_match.group(1).strip() if title_match else "Blog Post"
    # Clean up title
    page_title = page_title.split('|')[0].strip()

    # 2. Extract Background Image URL from CSS
    # Look for .post-hero { ... background: ... url('...') ... }
    # We'll look for the background line specifically
    bg_match = re.search(r"background:\s*linear-gradient[^;]+url\(['\"]?([^'\")]+)['\"]?\)", content)
    
    if not bg_match:
        print(f"Skipping {filename} (No background image found in CSS)")
        # Try finding just url(...) if linear-gradient is missing or different
        bg_match = re.search(r"background-image:\s*url\(['\"]?([^'\")]+)['\"]?\)", content)
        
    if not bg_match:
         print(f"Skipping {filename} (Could not extract image URL)")
         return

    image_url = bg_match.group(1)
    
    # 3. Modify CSS: Remove the background line
    # We will comment it out or remove it to be safe.
    # Let's replace the whole match with "background: none;" to be clean, or just remove the image part.
    # Actually, the user wants the GRADIENT overlay kept. The previous refactor put the gradient in a separate div `.hero-overlay`.
    # So we should remove the background property entirety from CSS because we add the overlay div in HTML.
    
    # Locate the full background line
    full_bg_line = bg_match.group(0)
    content = content.replace(full_bg_line, "background: none")

    # 4. Modify HTML: Inject <img> and classes
    # Pattern: <section class="post-hero"> ... <div class="container">
    pattern = r'(<section class="post-hero">)\s*<div class="container">'
    
    # Replacement
    replacement = f"""<section class="post-hero relative-container" style="background: none;">
      <img src="{image_url}" alt="{page_title}" class="hero-bg-img" loading="eager">
      <div class="hero-overlay"></div>
      <div class="container hero-content-z">"""
      
    if "relative-container" in content:
        print(f"Skipping {filename} (Already refactored HTML)")
    else:
        content = re.sub(pattern, replacement, content, count=1)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Refactored {filename} -> Image: {image_url}")

if __name__ == "__main__":
    for file in TARGET_FILES:
        refactor_blog_post(file)
