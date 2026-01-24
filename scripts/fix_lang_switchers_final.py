
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def get_counterpart_path(filepath):
    """
    Calculates the relative path to the counterpart file.
    EN: /path/to/file.html -> DE: /path/to/de/file.html
    DE: /path/to/de/file.html -> EN: /path/to/file.html
    """
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    
    if rel_path.startswith('de' + os.sep) or rel_path == 'de':
        # German -> English
        # Strip 'de/' prefix
        if rel_path.startswith('de' + os.sep):
            target_rel = rel_path[3:]
        else:
            # de/index.html presumably (if we are in de dir? wait os.walk gives root relative)
            target_rel = 'index.html' # Fallback? No. de/index.html -> index.html
            
        # Case for de/index.html -> index.html
        if rel_path == os.path.join('de', 'index.html'):
            target_rel = 'index.html'
            
        # Target needs to be relative to current file
        # Current file is in de/
        # So we need ../ + target_rel
        # But wait, if target_rel is blog-posts/foo.html, we need ../blog-posts/foo.html
        
        # Robust way: 
        # 1. Determine absolute path of target
        target_abs = os.path.join(ROOT_DIR, target_rel)
        
        # 2. Compute relative path from current file's directory
        current_dir = os.path.dirname(filepath)
        final_href = os.path.relpath(target_abs, current_dir)
        
        return final_href, "EN"

    else:
        # English -> German
        # Add 'de/' prefix
        # But if it's index.html, it goes to de/index.html (or just de/?)
        # Let's target the FILE de/index.html to be safe for local dev
        
        target_rel = os.path.join('de', rel_path)
        
        # 1. Determine absolute path of target
        target_abs = os.path.join(ROOT_DIR, target_rel)
        
        # 2. Compute relative path
        current_dir = os.path.dirname(filepath)
        final_href = os.path.relpath(target_abs, current_dir)
        
        return final_href, "DE"

def fix_switcher(filepath):
    # Skip if file doesn't exist (deleted ones)
    if not os.path.exists(filepath): return

    correct_href, target_lang = get_counterpart_path(filepath)
    
    # Check if counterpart exists?
    # Actually, we should check. If it doesn't exist (e.g. admin page), maybe we shouldn't break it/change it?
    # Or we construct it anyway. 
    # Let's verify existence of target absolute path.
    target_abs = os.path.normpath(os.path.join(os.path.dirname(filepath), correct_href))
    if not os.path.exists(target_abs):
        print(f"Skipping {filepath}: Target {target_abs} does not exist.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # Regex to find the switcher link
    # German page: Link text is EN
    # English page: Link text is DE
    
    # We look for <a ...>EN</a> or <a ...>DE</a>
    # We want to replace the href attribute.
    
    # Pattern: (<a\s+href=["\'])([^"\']*)(["\'][^>]*>\s*TEXT\s*</a>)
    # TEXT is target_lang
    
    pattern = re.compile(f'(<a\\s+href=["\'])([^"\']*)(["\'][^>]*>\\s*{target_lang}\\s*</a>)', re.IGNORECASE)
    
    # Replacement: group 1 + correct_href + group 3
    new_content = pattern.sub(f'\\1{correct_href}\\3', content)
    
    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {target_lang} switcher in: {filepath} -> {correct_href}")

def main():
    print("Fixing Language Switchers...")
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'scripts' in dirs: dirs.remove('scripts')
        
        for file in files:
            if file.endswith('.html'):
                fix_switcher(os.path.join(root, file))

if __name__ == "__main__":
    main()
