
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def get_de_link(filepath):
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    
    # If we are in the 'de' folder, we skip (this script is for EN pages)
    if rel_path.startswith('de' + os.sep) or rel_path == 'de':
        return None
        
    # Calculate depth
    depth = rel_path.count(os.sep)
    
    # Target DE path relative to ROOT is de/rel_path
    # But we need it relative to current file.
    # From current file, we go up 'depth' times to root, then into 'de', then to 'rel_path'
    
    # Example: index.html -> de/index.html
    # Example: about.html -> de/about.html
    # Example: blog-posts/post.html -> ../de/blog-posts/post.html
    
    prefix = "../" * depth
    target = f"{prefix}de/{rel_path}"
    return target

def add_switcher(filepath):
    # Only process .html files
    if not filepath.endswith('.html'):
        return

    # Skip if inside /de/ directory
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    if rel_path.startswith('de/') or rel_path == 'de':
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if switcher already exists
    if 'class="lang-switch"' in content:
        print(f"Skipping {filepath}: Switcher already exists.")
        return

    # Prepare Switcher HTML
    de_link = get_de_link(filepath)
    if not de_link:
        return

    switcher_html = f'''
        <div class="lang-switch"
          style="display: inline-flex; gap: 6px; margin-left: 10px; margin-right: 10px; align-items: center; font-weight: 500; font-size: 0.95rem;">
          <span style="color: white; border-bottom: 2px solid var(--accent-start); padding-bottom: 2px;">EN</span>
          <span style="color: rgba(255,255,255,0.4);">|</span>
          <a href="{de_link}" style="color: rgba(255,255,255,0.7); text-decoration: none; transition: color 0.2s;">DE</a>
        </div>
        '''

    # Find insertion point: Before the CTA button
    # Pattern: <a href="..." class="btn-header-cta">
    cta_pattern = re.compile(r'(<a\s+href="[^"]*"\s+class="btn-header-cta"[^>]*>)')
    
    match = cta_pattern.search(content)
    if match:
        # Insert before the match
        new_content = content[:match.start()] + switcher_html.strip() + match.group(0) + content[match.end():]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Added switcher to: {filepath}")
    else:
        print(f"Skipping {filepath}: CTA button not found.")

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        # Exclude 'de' dir from traversal to avoid processing German files
        if 'de' in dirs:
            # We don't remove it here because os.walk is recursive, but we check rel_path in add_switcher
            pass
            
        for file in files:
            add_switcher(os.path.join(root, file))

if __name__ == "__main__":
    main()
