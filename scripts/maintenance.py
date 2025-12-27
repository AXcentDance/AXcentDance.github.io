import os
import re

def minify_css(content):
    # Remove comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    # Remove whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*([:;{}])\s*', r'\1', content)
    return content.strip()

def minify_js(content):
    # Simple JS minification (removes comments and extra whitespace)
    # Note: This is a basic minifier. For production complexities, a proper tool is recommended.
    # Remove single line comments
    content = re.sub(r'//.*', '', content)
    # Remove multi-line comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    # Remove whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*([=+\-*/{}();,])\s*', r'\1', content)
    return content.strip()

def strip_html(content):
    # Remove script and style tags and their content
    content = re.sub(r'<script[\s\S]*?</script>', '', content)
    content = re.sub(r'<style[\s\S]*?</style>', '', content)
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', ' ', content)
    # Decode HTML entities (basic)
    content = content.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    return content

def generate_llms_full(root_dir, output_file):
    print(f"Generating {output_file}...")
    
    files_to_process = [
        ('index.html', 'Home'),
        ('schedule.html', 'Class Schedule'),
        ('events.html', 'Events & Workshops'),
        ('about.html', 'About Us'),
        ('contact.html', 'Contact Us'),
        ('private-lessons.html', 'Private Lessons'),
        ('wedding-dance.html', 'Wedding Dance'),
        ('room-rental.html', 'Room Rental'),
        ('class-bachata-beginner-0.html', 'Bachata Beginner 0'),
        ('class-bachata-sensual-foundation.html', 'Bachata Sensual Foundation'),
        ('beginner-guide.html', 'Beginner Guide'),
        ('etiquette.html', 'Dance Etiquette'),
        ('corporate-events.html', 'Corporate Events'),
        ('faq.html', 'FAQ'),
        ('gallery.html', 'Gallery'),
    ]

    full_content = "# AXcent Dance Website - Full Content\n\n"

    for filename, title in files_to_process:
        filepath = os.path.join(root_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                clean_content = strip_html(content)
                full_content += f"\n---\n\n# Page: {title} ({filename})\n\n"
                # Format content a bit to be more readable than just a single line
                # Break long lines? formatting is tricky without advanced parsing.
                # Let's just put the cleaned content.
                # Actually, simply stripping all tags makes it a blob of text. 
                # Preserving headers could be better but regex is fragile.
                # The previous llms-full.txt seemed to preserve structure well. 
                # It might have been manual or using a better tool like pandoc or a standard text browser dump (like `lynx -dump`).
                # Since we don't have lynx, we will try to be slightly smarter or accept potential quality drop.
                # Let's stick to simple stripping for now as per instructions "update the ... llms-full".
                full_content += clean_content + "\n"
        else:
            print(f"Warning: {filename} not found.")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_content)
    print("Done generating llms-full.txt")

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Minify CSS
    css_path = os.path.join(root_dir, 'style.css')
    min_css_path = os.path.join(root_dir, 'style.min.css')
    if os.path.exists(css_path):
        print("Minifying style.css...")
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        min_css = minify_css(css_content)
        with open(min_css_path, 'w', encoding='utf-8') as f:
            f.write(min_css)
    
    # Minify JS
    js_path = os.path.join(root_dir, 'script.js')
    min_js_path = os.path.join(root_dir, 'script.min.js')
    if os.path.exists(js_path):
        print("Minifying script.js...")
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        min_js = minify_js(js_content)
        with open(min_js_path, 'w', encoding='utf-8') as f:
            f.write(min_js)

    # Generate llms-full.txt
    generate_llms_full(root_dir, os.path.join(root_dir, 'llms-full.txt'))

if __name__ == '__main__':
    main()
