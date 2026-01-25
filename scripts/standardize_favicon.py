
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def standardize_favicon(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Update/Inject Apple Touch Icon
    # Expected: <link rel="apple-touch-icon" href="/apple-touch-icon-v2.png">
    
    apple_pattern = re.compile(r'<link\s+rel=["\']apple-touch-icon["\']\s+href=["\'][^"\']+["\']\s*>', re.IGNORECASE)
    expected_apple = '<link rel="apple-touch-icon" href="/apple-touch-icon-v2.png">'
    
    if apple_pattern.search(content):
        # Update existing
        content = apple_pattern.sub(expected_apple, content)
    else:
        # Inject? Usually before/after icon. Let's stick to updating favicon first as requested.
        pass

    # 2. Update Favicon
    # Expected: <link rel="icon" href="/favicon-v2.png" type="image/png">
    # Variations: rel="shortcut icon", rel="icon", differenthrefs.
    
    # regex for any icon link
    # <link rel="(shortcut )?icon" href="..." ...>
    
    icon_pattern = re.compile(r'<link\s+rel=["\'](?:shortcut\s+)?icon["\']\s+href=["\']([^"\']+)["\'](?:\s+type=["\'][^"\']+["\'])?\s*>', re.IGNORECASE)
    
    expected_icon = '<link rel="icon" href="/favicon-v2.png" type="image/png">'
    
    # Check if we have one
    match = icon_pattern.search(content)
    if match:
        current_href = match.group(1)
        # If it's already perfect, skip
        # Note: we might want to enforce the whole tag structure too (type=image/png)
        full_match = match.group(0)
        
        # We replace the entire tag with our standard tag
        if full_match.strip() != expected_icon.strip():
            content = content.replace(full_match, expected_icon)
            print(f"Updated favicon in: {os.path.basename(filepath)}")
    else:
        # Insert it if missing?
        # Find </head> and insert before
        head_end = re.search(r'</head>', content, re.IGNORECASE)
        if head_end:
            content = content[:head_end.start()] + '  ' + expected_icon + '\n' + content[head_end.start():]
            print(f"Inserted favicon in: {os.path.basename(filepath)}")

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'scripts' in dirs: dirs.remove('scripts')
        
        for file in files:
            if file.endswith('.html'):
                standardize_favicon(os.path.join(root, file))

if __name__ == "__main__":
    main()
