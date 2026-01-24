
import os
import re

BLOG_DIR = '/Users/slamitza/AXcentWebsiteGitHub/de/blog-posts'

def fix_image_paths(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Strategy:
    # We want to replace all occurrences of "../assets/" with "../../assets/"
    # BUT we must avoid turning "../../assets/" into "../../../assets/" if we run this multiple times
    # or if some were already fixed.
    
    # Regex lookbehind is one way, or just a two-step process.
    # Step 1: Replace all "../../assets/" with a placeholder (to protect already correct ones)
    # Step 2: Replace all "../assets/" with "../../assets/"
    # Step 3: Replace placeholder back to "../../assets/"
    
    PLACEHOLDER = "___ALREADY_FIXED_ASSETS___"
    
    # Temporarily hide correct paths
    content = content.replace('../../assets/', PLACEHOLDER)
    
    # Fix incorrect paths (including those in the middle of srcset)
    content = content.replace('../assets/', '../../assets/')
    
    # Restore correct paths (which were hidden)
    content = content.replace(PLACEHOLDER, '../../assets/')
    
    # Handle Favicons/Apple Touch Icons which might be absolute /assets or relative ../
    # Previous script handled some, but let's be thorough.
    # Using same logic for favicon if they are in root assets/ or root.
    # Typically favicons are at root: /favicon.png or ../favicon.png (from English blog).
    # From de/blog-posts/ (depth 2), we need ../../favicon.png
    
    PLACEHOLDER_FAV = "___ALREADY_FIXED_FAV___"
    content = content.replace('../../favicon', PLACEHOLDER_FAV)
    content = content.replace('../../apple-touch-icon', PLACEHOLDER_FAV)
    
    content = content.replace('../favicon', '../../favicon')
    content = content.replace('../apple-touch-icon', '../../apple-touch-icon')
    
    content = content.replace(PLACEHOLDER_FAV, '../../favicon')
    content = content.replace(PLACEHOLDER_FAV, '../../apple-touch-icon') # Should work if placeholder unique

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed paths in: {filepath}")
    else:
        print(f"No changes needed for: {filepath}")

def main():
    if not os.path.exists(BLOG_DIR):
        print(f"Directory not found: {BLOG_DIR}")
        return

    for filename in os.listdir(BLOG_DIR):
        if filename.endswith(".html"):
            fix_image_paths(os.path.join(BLOG_DIR, filename))

if __name__ == "__main__":
    main()
