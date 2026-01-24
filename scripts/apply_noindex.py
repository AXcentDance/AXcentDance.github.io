
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

# Pages that should be noindex, nofollow
TARGET_PAGES = [
    'thank-you.html',
    'thank-you-contact.html',
    'thank-you-trial.html',
    '404.html',
    'cart.html'
]

def apply_noindex(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find existing robots meta
    # <meta name="robots" content="...">
    
    robots_pattern = re.compile(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']', re.IGNORECASE)
    
    match = robots_pattern.search(content)
    new_tag = '<meta name="robots" content="noindex, nofollow">'
    
    if match:
        current_content = match.group(1)
        if current_content.lower() == 'noindex, nofollow':
            print(f"Skipping {filepath}: Already noindex, nofollow.")
            return

        # Replace existing tag
        new_content = content.replace(match.group(0), new_tag)
        print(f"Updated {filepath}: {current_content} -> noindex, nofollow")
    else:
        # Insert new tag
        # Look for <head> or similar safe place.
        # After <meta charset> is good.
        
        charset_match = re.search(r'<meta\s+charset=["\'][^"\']+["\']\s*>', content, re.IGNORECASE)
        if charset_match:
            new_content = content[:charset_match.end()] + '\n    ' + new_tag + content[charset_match.end():]
            print(f"Added to {filepath}: noindex, nofollow")
        else:
            # Fallback: Just insert after <head>
            head_match = re.search(r'<head>', content, re.IGNORECASE)
            if head_match:
                new_content = content[:head_match.end()] + '\n    ' + new_tag + content[head_match.end():]
                print(f"Added to {filepath}: noindex, nofollow (fallback)")
            else:
                print(f"Skipping {filepath}: No <head> found.")
                return

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file in TARGET_PAGES: # Matches filename exactly (thank-you.html)
                # Apply to EN and DE (since loop walks everything)
                filepath = os.path.join(root, file)
                apply_noindex(filepath)

if __name__ == "__main__":
    main()
