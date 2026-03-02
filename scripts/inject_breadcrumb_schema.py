
import os
import re
import json

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def get_breadcrumb_schema(file_path, title, lang):
    # Determine base URL
    base_url = "https://axcentdance.com"
    
    # Breadcrumb names
    home_name = "Startseite" if lang == "de" else "Home"
    blog_name = "Blog" # Same in both
    
    # Item URLs
    home_url = f"{base_url}/de/" if lang == "de" else f"{base_url}/"
    blog_url = f"{base_url}/blog" # Blog page is shared or has its own logic? 
    # Actually, in existence: blog is https://axcentdance.com/blog for both? 
    # Let's check blog.html
    
    # Post URL - Remove .html for clean URL
    rel_path = os.path.relpath(file_path, ROOT_DIR).replace('\\', '/')
    clean_slug = rel_path.replace('.html', '')
    post_url = f"{base_url}/{clean_slug}"

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": home_name,
                "item": home_url
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": blog_name,
                "item": blog_url
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": title,
                "item": post_url
            }
        ]
    }
    return schema

def inject_breadcrumb(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already exists
    if '"@type": "BreadcrumbList"' in content or '"@type":"BreadcrumbList"' in content:
        return False

    # Language
    lang = "de" if "/de/" in file_path.replace('\\', '/') else "en"
    
    # Extract Title
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if not title_match:
        return False
    
    # Clean Title (remove site name suffix)
    title = title_match.group(1).split('|')[0].strip()

    schema = get_breadcrumb_schema(file_path, title, lang)
    schema_json = json.dumps(schema, indent=4, ensure_ascii=False)
    
    script_tag = f'\n    <script type="application/ld+json">\n    {schema_json}\n    </script>'

    # Insertion point: before </head> or after existing schema
    if '</head>' in content:
        new_content = content.replace('</head>', f'{script_tag}\n</head>')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def main():
    print("Injecting Breadcrumb JSON-LD into blog posts...")
    blog_dirs = [
        os.path.join(ROOT_DIR, 'blog-posts'),
        os.path.join(ROOT_DIR, 'de/blog-posts')
    ]
    
    count = 0
    for blog_dir in blog_dirs:
        if not os.path.exists(blog_dir): continue
        for root, dirs, files in os.walk(blog_dir):
            for file in files:
                if file.endswith(".html"):
                    if inject_breadcrumb(os.path.join(root, file)):
                        print(f"[INJECTED] {file}")
                        count += 1
    
    print(f"Finished. Injected schema into {count} files.")

if __name__ == "__main__":
    main()
