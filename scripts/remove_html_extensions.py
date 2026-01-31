
import os
import re

def remove_html_extensions(directory):
    """
    Recursively remove .html extension from internal links in all HTML files.
    """
    # Regex to find href="... .html" but ignore external links (http/https) and anchors
    # It captures:
    # Group 1: href=" or href='
    # Group 2: The filename part
    # Group 3: .html
    # Group 4: Optional anchor (#...)
    # Group 5: Closing quote
    
    # We want to match: href="page.html" -> href="page"
    # match: href="./page.html" -> href="./page"
    # match: href="folder/page.html" -> href="folder/page"
    
    pattern = re.compile(r'(href=["\'])(?!http|https|//|#)([^"\']+\.html)(["\'])')
    
    # helper for replacement
    def replacer(match):
        prefix = match.group(1)
        full_path = match.group(2)
        suffix = match.group(3) # This is the closing quote
        
        # Check if it ends in .html
        if full_path.endswith('.html'):
             # Replace only the last occurrence of .html
             new_path = full_path[:-5] 
             
             # Special case: index.html -> ./
             if new_path == "index" or new_path.endswith("/index"):
                 if new_path == "index":
                     new_path = "./"
                 else:
                     new_path = new_path[:-5] # remove "index" -> leave folder/
                     
             return f"{prefix}{new_path}{suffix}"
        return match.group(0)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Careful replacement
                # We also need to handle Canonical tags: <link rel="canonical" href="... .html" />
                # But typically those are absolute URLs. Let's do a separate regex for canonical if needed.
                # For now, let's focus on relative internal links.
                
                # Also handle canonical definition within the head often looks like:
                # <link rel="canonical" href="https://axcentdance.com/page.html" />
                # We should strip .html from there too.
                
                canonical_pattern = re.compile(r'(<link\s+rel=["\']canonical["\']\s+href=["\'])(.*?\.html)(["\'])')
                
                def canonical_replacer(match):
                    prefix = match.group(1)
                    url = match.group(2)
                    suffix = match.group(3)
                    if url.endswith('.html'):
                         return f"{prefix}{url[:-5]}{suffix}"
                    return match.group(0)

                new_content = pattern.sub(replacer, content)
                new_content = canonical_pattern.sub(canonical_replacer, new_content)
                
                if new_content != content:
                    print(f"Updating {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == "__main__":
    remove_html_extensions(".")
