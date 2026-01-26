import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# Configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, 'llms-full.txt')

# Files to ignore
IGNORE_PATTERNS = [
    'node_modules', '.git', 'tmp', '.gemini', '__pycache__', 'scripts',
    'google', 'google', 'assets' # Ignore assets folder if it accidentally has html
]

# Order priority (filenames containing these strings come first)
PRIORITY = [
    'index.html',
    'schedule.html',
    'registration.html',
    'cart.html',
    'events.html',
    'about.html',
    'contact.html'
]

def should_ignore(path):
    for pattern in IGNORE_PATTERNS:
        if pattern in path.split(os.sep):
            return True
    return False

def get_file_priority(filename):
    # Lower index = higher priority
    for i, p in enumerate(PRIORITY):
        if filename == p:
            return i
    # Default priority for others
    if 'blog-posts' in filename:
        return 100
    if 'de/' in filename:
        return 50 # German content after main English content
    return 10

def clean_text(text):
    # Collapse whitespace
    return re.sub(r'\s+', ' ', text).strip()

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract Title
        title = soup.title.string.strip() if soup.title else "No Title"
        
        # Extract Meta Description
        meta_desc = ""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            meta_desc = meta['content'].strip()
            
        # Extract Body Text
        # Remove scripts and styles first
        for script in soup(["script", "style", "noscript", "iframe", "svg"]):
            script.extract()
            
        # Get text
        text = soup.get_text(separator=' ')
        clean_body = clean_text(text)
        
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        
        return {
            'path': rel_path,
            'title': title,
            'description': meta_desc,
            'content': clean_body
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    print(f"Scanning {ROOT_DIR} for HTML files...")
    
    html_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        if should_ignore(root):
            continue
            
        for file in files:
            if file.endswith('.html'):
                full_path = os.path.join(root, file)
                if not should_ignore(full_path):
                    html_files.append(full_path)
    
    print(f"Found {len(html_files)} HTML files.")
    
    # Sort files
    def sort_key(path):
        rel = os.path.relpath(path, ROOT_DIR)
        priority = get_file_priority(rel)
        # Secondary sort by name
        return (priority, rel)
        
    html_files.sort(key=sort_key)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        out.write("# AXcent Dance Website - Full Content\n")
        out.write(f"# Generated automatically. Total Pages: {len(html_files)}\n\n")
        out.write("---\n\n")
        
        for file_path in html_files:
            data = process_file(file_path)
            if data:
                print(f"Writing {data['path']}...")
                out.write(f"# Page: {data['title']} ({data['path']})\n")
                if data['description']:
                    out.write(f"Description: {data['description']}\n")
                out.write("\n")
                out.write(data['content'])
                out.write("\n\n---\n\n")
                
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
