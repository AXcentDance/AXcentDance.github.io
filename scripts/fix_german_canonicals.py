import os
import re

# Directory to process
de_root = "/Users/slamitza/AXcentWebsiteGitHub/de"

for root, dirs, files in os.walk(de_root):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the canonical link
            canonical_match = re.search(r'<link rel=["\']canonical["\'] href=["\']([^"\']+)["\']', content)
            
            if canonical_match:
                canonical_url = canonical_match.group(1)
                
                # Check if it already contains /de/
                if "https://axcentdance.com/de/" not in canonical_url:
                    # Replace axcentdance.com/ with axcentdance.com/de/
                    # Special case for index.html as homepage
                    if canonical_url == "https://axcentdance.com/":
                        new_canonical = "https://axcentdance.com/de/"
                    else:
                        new_canonical = canonical_url.replace("https://axcentdance.com/", "https://axcentdance.com/de/")
                    
                    if new_canonical != canonical_url:
                        updated_content = content.replace(canonical_url, new_canonical)
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        print(f"Updated {path}: {canonical_url} -> {new_canonical}")
