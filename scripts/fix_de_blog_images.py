
import os
import re

BLOG_DIR = '/Users/slamitza/AXcentWebsiteGitHub/de/blog-posts'

def fix_image_paths(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Fix standard image sources
    # Matches src="../assets/" and replaces with src="../../assets/"
    # We want to be careful not to replace something that is already ../../
    
    # Strategy: 
    # Replace all `src="../assets"` with `src="../../assets"`
    # Then check if we created `src="../../../assets"` (if it was already correct) and revert that?
    # No, better regex.
    
    # Pattern: src=" followed by exactly one dot and slash and assets
    # src="\./assets" -> src="../../assets"  (if it was local)
    # src="\.\./assets" -> src="../../assets" (most likely case if copied from EN blog which is one level deep)
    
    # English blog: /blog-posts/post.html -> ../assets/image.jpg
    # German blog: /de/blog-posts/post.html -> ../../assets/image.jpg
    
    # So we want to change `../assets` to `../../assets`
    content = content.replace('src="../assets', 'src="../../assets')
    content = content.replace('srcset="../assets', 'srcset="../../assets')
    
    # Also Check Favicons which might be `href="/favicon..."` (Absolute) or `href="../favicon..."`
    # English: href="/favicon.png" or href="../favicon.png"
    # If absolute, `scripts/fix_root_links.py` might not have touched these unless targeted.
    # Let's make them relative: `../../favicon`
    
    content = content.replace('href="/apple-touch-icon', 'href="../../apple-touch-icon')
    content = content.replace('href="/favicon', 'href="../../favicon')
    
    # If we accidentally made triple dots from double run?
    content = content.replace('src="../../../assets', 'src="../../assets')
    content = content.replace('srcset="../../../assets', 'srcset="../../assets')
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed paths in: {filepath}")

def main():
    if not os.path.exists(BLOG_DIR):
        print(f"Directory not found: {BLOG_DIR}")
        return

    for filename in os.listdir(BLOG_DIR):
        if filename.endswith(".html"):
            fix_image_paths(os.path.join(BLOG_DIR, filename))

if __name__ == "__main__":
    main()
