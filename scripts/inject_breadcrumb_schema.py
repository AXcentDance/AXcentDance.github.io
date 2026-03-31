
import os
import re
import json

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def get_breadcrumb_data(file_path, title, lang):
    base_url = "https://axcentdance.com"
    home_name = "Startseite" if lang == "de" else "Home"
    blog_name = "Blog"
    
    home_url = f"{base_url}/de/" if lang == "de" else f"{base_url}/"
    blog_url = f"{base_url}/blog" 
    
    rel_path = os.path.relpath(file_path, ROOT_DIR).replace('\\', '/')
    clean_slug = rel_path.replace('.html', '').replace('index', '')
    if clean_slug.endswith('/'): clean_slug = clean_slug[:-1]
    post_url = f"{base_url}/{clean_slug}"

    return {
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

def inject_breadcrumb(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lang = "de" if "/de/" in file_path.replace('\\', '/') else "en"
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if not title_match: return False
    title = title_match.group(1).split('|')[0].strip()

    breadcrumb_item = get_breadcrumb_data(file_path, title, lang)

    # Find the main @graph script tag
    graph_match = re.search(r'<script type="application/ld\+json">\s*(\{.*?"@graph":\s*\[.*?\]\s*\})\s*</script>', content, re.DOTALL)
    
    # Also find and remove any standalone BreadcrumbList scripts to prevent duplication
    standalone_re = re.compile(r'\n?\s*<script type="application/ld\+json">.*?"@type":\s*"BreadcrumbList".*?</script>', re.DOTALL)
    content = standalone_re.sub('', content)

    if graph_match:
        try:
            full_json = json.loads(graph_match.group(1))
            graph = full_json.get("@graph", [])
            
            # Remove existing BreadcrumbList
            graph = [item for item in graph if item.get("@type") != "BreadcrumbList"]
            graph.append(breadcrumb_item)
            
            # --- GOOGLE DISCOVER AUTO-OPTIMIZATION [NEW] ---
            # Automatically update images to 1200px and update dateModified
            has_update = False
            for item in graph:
                if item.get("@id") and any(suffix in item.get("@id") for suffix in ["#blogposting", "#article"]):
                    # 1. Standardize Image dimensions (1200px)
                    if "image" in item:
                        img = item["image"]
                        if isinstance(img, dict) and img.get("@type") == "ImageObject":
                            if img.get("width") != 1200:
                                img["width"] = 1200
                                has_update = True
                                print(f"  [DISCOVER] Forced 1200px width for: {img.get('url', 'unknown')}")
                            if not img.get("height"):
                                img["height"] = 1200 # Default to square if missing
                                has_update = True

                    # 2. Update dateModified (Freshness)
                    if item.get("dateModified") != "2026-03-31":
                        item["dateModified"] = "2026-03-31"
                        has_update = True
                        print(f"  [FRESHNESS] Updated dateModified to 2026-03-31")

                    # 3. Ensure recprocity (mainEntityOfPage)
                    if "#webpage" in item.get("mainEntityOfPage", {}).get("@id", ""):
                        pass # Valid binding
                    else:
                        item["mainEntityOfPage"] = {"@id": f"{post_url}#webpage"}
                        has_update = True

            full_json["@graph"] = graph
            new_json_str = json.dumps(full_json, indent=2, ensure_ascii=False)
            new_script = f'<script type="application/ld+json">\n{new_json_str}\n</script>'
            
            # Re-find graph start because content might have shifted due to standalone removal
            graph_match = re.search(r'<script type="application/ld\+json">\s*(\{.*?"@graph":\s*\[.*?\]\s*\})\s*</script>', content, re.DOTALL)
            if graph_match:
                content = content[:graph_match.start()] + new_script + content[graph_match.end():]
            else:
                # If removal broke the match, just append to head (safe fallback)
                content = content.replace('</head>', f'{new_script}\n</head>')
                
        except json.JSONDecodeError:
            return False
    else:
        # No @graph - creating a standalone script but as a @graph for future compatibility
        full_json = {
            "@context": "https://schema.org",
            "@graph": [breadcrumb_item]
        }
        new_json_str = json.dumps(full_json, indent=2, ensure_ascii=False)
        new_script = f'\n  <script type="application/ld+json">\n{new_json_str}\n  </script>\n'
        content = content.replace('</head>', f'{new_script}</head>')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def main():
    print("Injecting Unified Breadcrumb JSON-LD (@graph) into blog posts...")
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
                        print(f"[REFACTORED] {file}")
                        count += 1
    
    print(f"Finished. Synced {count} files to Unified Schema standard.")

if __name__ == "__main__":
    main()
