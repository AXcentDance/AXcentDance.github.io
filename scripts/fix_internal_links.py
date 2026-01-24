
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

# List of exact hrefs to replace. 
# We target `href="VALUE"` and `href='VALUE'`
# We map VALUE -> VALUE.html
LINK_MAP = [
    "about", "schedule", "registration", "events", "contact",
    "room-rental", "corporate-events", "wedding-dance", "private-lessons",
    "gallery", "education", "beginner-guide", "blog", "faq", "etiquette",
    "guide-bachata", "terms", "privacy", "imprint"
]

# Simple replacements (just appending .html)
REPLACEMNTS = {f'href="{link}"': f'href="{link}.html"' for link in LINK_MAP}
REPLACEMNTS.update({f"href='{link}'": f"href='{link}.html'" for link in LINK_MAP})

# Specific case for blog posts if they are linked without .html
# We saw `href="blog-posts/roots-of-bachata"` in the footer of de/index.html
REPLACEMNTS['href="blog-posts/roots-of-bachata"'] = 'href="blog-posts/roots-of-bachata.html"'

def fix_links_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for old, new in REPLACEMNTS.items():
        content = content.replace(old, new)
        
    # Also handle localized links if they exist as absolute paths or relative with /de/ prefix?
    # The user request specifically mentioned: `href="about"` in a file at `de/bachata-sensual-foundation.html`
    # resolving to `.../de/about`.
    # So simple string replacement of `href="about"` matches.
    
    if content != original_content:
        print(f"Fixed links in: {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".html"):
                fix_links_in_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
