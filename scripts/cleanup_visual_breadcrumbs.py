import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

# Find all blog post files
blog_posts = []
for root, dirs, files in os.walk(ROOT_DIR):
    if "blog-posts" in root:
        for f in files:
            if f.endswith(".html"):
                blog_posts.append(os.path.join(root, f))

def cleanup_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find the visual breadcrumb block
    # It starts with an optional comment and then the <nav class="breadcrumb-nav"> ... </nav>
    breadcrumb_regex = re.compile(r'(\s*<!-- Visual Breadcrumb -->)?\s*<nav class="breadcrumb-nav".*?</nav>', re.DOTALL | re.IGNORECASE)
    
    new_content, count = breadcrumb_regex.subn('', content)
    
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Removed {count} breadcrumb block(s) from {file_path}")
    else:
        # Check if maybe it doesn't have the class breadcrumb-nav but is still there
        if 'breadcrumb-list' in content:
             print(f"Warning: Found breadcrumb-list but no breadcrumb-nav in {file_path}")

for post in blog_posts:
    cleanup_file(post)
