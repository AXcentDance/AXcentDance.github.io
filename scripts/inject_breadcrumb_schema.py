
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
    blog_url = f"{base_url}/blog" 
    
    # Post URL - Remove .html for clean URL
    rel_path = os.path.relpath(file_path, ROOT_DIR).replace('\\', '/')
    clean_slug = rel_path.replace('.html', '')
    post_url = f"{base_url}/{clean_slug}"

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "inLanguage": lang,
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

    # Skip ONLY if BreadcrumbList already has inLanguage
    # Use re.SEARCH to see if "BreadcrumbList" and "inLanguage" appear close together
    up_to_date_re = re.compile(r'"@type":\s*"BreadcrumbList".*?"inLanguage"', re.DOTALL)
    if up_to_date_re.search(content):
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

    # Case 1: Already exists inside a @graph array (Standard premium structure)
    graph_breadcrumb_re = re.compile(r'(\s*\{\s*"@type":\s*"BreadcrumbList",)', re.IGNORECASE)
    if graph_breadcrumb_re.search(content):
        print(f"Updating @graph breadcrumb in {os.path.basename(file_path)}...")
        # Inject "inLanguage" after the @type line
        new_content = graph_breadcrumb_re.sub(r'\1\n        "inLanguage": "' + lang + '",', content)
    
    # Case 2: Exists as a separate script tag (Legacy or alternative structure)
    else:
        breadcrumb_script_re = re.compile(r'\n?\s*<script type="application/ld\+json">.*?"@type":\s*"BreadcrumbList".*?</script>', re.DOTALL)
        if breadcrumb_script_re.search(content):
            print(f"Updating standalone breadcrumb in {os.path.basename(file_path)}...")
            new_content = breadcrumb_script_re.sub(f'\n    {script_tag}', content)
        elif '</head>' in content:
            # Standard injection before closing head
            new_content = content.replace('</head>', f'{script_tag}\n</head>')
        else:
            return False

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

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
