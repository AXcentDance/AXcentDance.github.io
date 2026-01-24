
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'
INDEX_FILE = os.path.join(ROOT_DIR, 'index.html')

def get_master_footer_template():
    """
    Reads index.html, extracts the footer, and converts it into a template
    by replacing specific relative links with '{prefix}'.
    """
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract footer
    footer_pattern = re.compile(r'<footer class="main-footer">.*?</footer>', re.DOTALL)
    match = footer_pattern.search(content)
    
    if not match:
        raise Exception("Could not find footer in index.html")
        
    footer_html = match.group(0)
    
    # Now we need to convert "local" links in index.html to template placeholders.
    # In index.html (root), links are:
    # "guide-bachata.html", "schedule.html", "terms.html", etc.
    # We want to replace valid internal links with "{prefix}LINK"
    
    # List of files/links we expect to be relative
    # This list should match the links found in the footer
    # We can use regex to find href="..." and if it doesn't start with http/https/mailto, prepending {prefix}
    
    def replacer(m):
        href = m.group(1)
        quote = m.group(2) # " or '
        
        # Don't touch absolute links or anchors or empty
        if href.startswith(('http', 'https', 'mailto:', '//', '#')):
            return m.group(0)
        
        # Don't touch javascript:
        if href.startswith('javascript:'):
            return m.group(0)
            
        # If it's a file path like "guide-bachata.html" or "blog-posts/...", replace with "{prefix}..."
        # In index.html (root), these are relative to root.
        # So we just prepend {prefix}
        
        return f'href={quote}{{prefix}}{href}{quote}'

    # Regex for href attributes
    # href="VALUE" or href='VALUE'
    # We generally standardized on double quotes, but let's be safe.
    template = re.sub(r'href=(["\'])(.*?)\1', lambda m: replacer(re.match(r'href=(["\'])(.*?)\1', m.group(0))), footer_html)
    
    return template

def get_prefix(filepath):
    """
    Returns the relative prefix (e.g., "", "../", "../../") needed to get back to ROOT_DIR.
    """
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    depth = rel_path.count(os.sep)
    
    if depth == 0:
        return ""
    else:
        return "../" * depth

def propagate_footer(filepath, template):
    # Skip index.html itself (source)
    if os.path.abspath(filepath) == os.path.abspath(INDEX_FILE):
        return

    # Only process English pages (exclude /de/)
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    if rel_path.startswith('de' + os.sep) or rel_path == 'de':
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find existing footer
    footer_pattern = re.compile(r'<footer class="main-footer">.*?</footer>', re.DOTALL)
    
    match = footer_pattern.search(content)
    if match:
        prefix = get_prefix(filepath)
        new_footer = template.format(prefix=prefix)
        new_content = content.replace(match.group(0), new_footer)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated footer in: {filepath}")
    else:
        print(f"Skipping {filepath}: No footer found.")

def main():
    try:
        template = get_master_footer_template()
        print("Successfully extracted and templated footer from index.html")
    except Exception as e:
        print(f"Error: {e}")
        return

    for root, dirs, files in os.walk(ROOT_DIR):
        # Prevent walking into 'de'
        if 'de' in dirs:
            dirs.remove('de')
            
        for file in files:
            if file.endswith(".html"):
                propagate_footer(os.path.join(root, file), template)

if __name__ == "__main__":
    main()
