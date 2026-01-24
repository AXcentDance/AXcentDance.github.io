import os
import re

def fix_english_page(file_path, rel_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Base URL depends on the page
    filename = os.path.basename(rel_path)
    page_stub = filename.replace('.html', '')
    if page_stub == 'index':
        en_url = "https://axcentdance.com/"
        de_url = "https://axcentdance.com/de/"
    else:
        en_url = f"https://axcentdance.com/{page_stub}"
        de_url = f"https://axcentdance.com/de/{page_stub}"
        if 'blog-posts' in rel_path:
             en_url = f"https://axcentdance.com/blog-posts/{page_stub}"
             de_url = f"https://axcentdance.com/de/blog-posts/{page_stub}"

    hreflang_tags = f'''    <link rel="alternate" hreflang="en" href="{en_url}" />
    <link rel="alternate" hreflang="de" href="{de_url}" />
    <link rel="alternate" hreflang="x-default" href="{en_url}" />'''
    
    # Remove existing
    content = re.sub(r'\s*<link\s+rel=["\']alternate["\']\s+hreflang=.*?>', '', content, flags=re.I)
    
    # Insert new tags after canonical or viewport
    if '<link rel="canonical"' in content:
        content = re.sub(r'(<link rel=["\']canonical["\'].*?>)', rf'\1\n{hreflang_tags}', content, flags=re.I)
    else:
        content = re.sub(r'(<meta name=["\']viewport["\'].*?>)', rf'\1\n{hreflang_tags}', content, flags=re.I)

    if original_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed Hreflang in: {rel_path}")

def main():
    root_dir = '/Users/slamitza/AXcentWebsiteGitHub'
    
    # Root pages
    for file in os.listdir(root_dir):
        if file.endswith('.html'):
            fix_english_page(os.path.join(root_dir, file), file)
            
    # Blog posts
    blog_posts_dir = os.path.join(root_dir, 'blog-posts')
    if os.path.exists(blog_posts_dir):
        for file in os.listdir(blog_posts_dir):
            if file.endswith('.html'):
                rel_path = os.path.join('blog-posts', file)
                fix_english_page(os.path.join(blog_posts_dir, file), rel_path)

if __name__ == "__main__":
    main()
