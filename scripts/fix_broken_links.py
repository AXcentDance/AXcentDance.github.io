import os

def bulk_replace(root_dir):
    print("Starting bulk replacement...")
    count = 0
    
    replacements = [
        ('href="/favicon.png"', 'href="/favicon-v2.png"'),
        ('href="/apple-touch-icon.png"', 'href="/apple-touch-icon-v2.png"'),
        # Remove broken cookie consent lines
        ('<link rel="stylesheet" href="../assets/css/cookie-consent.css">', ''),
        ('<script src="../assets/js/cookie-consent.js" defer></script>', '')
    ]
    
    for root, dirs, files in os.walk(root_dir):
        if 'node_modules' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                for old, new in replacements:
                    new_content = new_content.replace(old, new)
                
                # Also clean up empty lines if we removed scripts
                # This is a simple clean up
                
                if new_content != content:
                    print(f"Updating {file}...")
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count += 1

    print(f"Updated {count} files.")

if __name__ == "__main__":
    bulk_replace(os.getcwd())
