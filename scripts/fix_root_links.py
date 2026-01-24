
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def get_relative_home_path(filepath):
    # Calculate depth relative to ROOT_DIR
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    depth = rel_path.count(os.sep)
    if depth == 0:
        return "index.html"
    return "../" * depth + "index.html"

def get_relative_de_home_path(filepath):
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    depth = rel_path.count(os.sep)
    # If in root, go to de/index.html
    if depth == 0:
        return "de/index.html"
    # If in de/, go to index.html
    if rel_path.startswith("de" + os.sep) and depth == 1:
        return "index.html"
    # If deeper in de/ (e.g. de/blog-posts/), go up
    if rel_path.startswith("de" + os.sep):
         return "../" * (depth - 1) + "index.html"
    
    # Fallback for other folders if any
    return "../" * depth + "de/index.html"

def fix_root_links_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # Determine correct relative paths
    home_link = get_relative_home_path(filepath) # For English Home
    de_home_link = get_relative_de_home_path(filepath) # For German Home
    
    # Define Replacements
    # We want to catch href="/" and href="/de/" and replace them with relative paths.
    # We need to be careful not to match partial strings if possible, but usually href="/" is distinctive.
    
    # 1. Fix Root Logo Links (English & General)
    # <a href="/" ...>
    content = content.replace('href="/"', f'href="{home_link}"')
    
    # 2. Fix German Logo Links
    # <a href="/de/" ...>
    content = content.replace('href="/de/"', f'href="{de_home_link}"')
    
    if content != original_content:
        print(f"Fixed root links in: {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".html"):
                fix_root_links_in_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
