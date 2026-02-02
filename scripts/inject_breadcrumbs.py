
import os
import re
import json

# Configuration: Define Hub Pages and Courses
COURSE_FILES = [
    "bachata-beginner-0.html",
    "bachata-beginner-2.html",
    "bachata-sensual-foundation.html",
    "bachata-sensual-improver.html",
    "bachata-sensual-inter-adv.html",
    "lady-styling.html",
    "private-lessons.html",   # arguably a service/course
    "wedding-dance.html"      # arguably a service/course
]

# Hub Definitions
# format: (Hub Name, Hub URL Suffix)
HUBS = {
    "en": {
        "schedule": ("Schedule", "schedule"),
        "blog": ("Blog", "blog")
    },
    "de": {
        "schedule": ("Stundenplan", "de/schedule"),
        "blog": ("Blog", "blog") # Using 'blog' as per de/blog.html if it exists, assume parallel structure
    }
}

ROOT_URL = "https://axcentdance.com/"

def get_page_title(content):
    """Extracts title from <title> tag, removing brand suffix if possible"""
    found = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if found:
        full_title = found.group(1).strip()
        # Clean up common suffixes
        clean_title = full_title.split("|")[0].strip()
        clean_title = clean_title.split("-")[0].strip() 
        return clean_title
    return "Page"

def generate_breadcrumb_json(lang, hub_key, page_title, relative_url):
    """Generates the JSON-LD dict"""
    
    # Root Item (Level 1)
    if lang == "de":
        items = [{
            "@type": "ListItem",
            "position": 1,
            "name": "Startseite",
            "item": ROOT_URL + "de/"
        }]
    else:
        items = [{
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": ROOT_URL
        }]

    current_pos = 2

    # Hub Item (Level 2) - Optional
    if hub_key:
        hub_name, hub_suffix = HUBS[lang][hub_key]
        items.append({
            "@type": "ListItem",
            "position": current_pos,
            "name": hub_name,
            "item": ROOT_URL + hub_suffix
        })
        current_pos += 1

    # Current Page Item (Level 3 or 2)
    # Ensure URL is absolute
    full_url = ROOT_URL + relative_url.lstrip("/")
    
    items.append({
        "@type": "ListItem",
        "position": current_pos,
        "name": page_title,
        "item": full_url
    })

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }

def process_file(filepath, root_dir):
    rel_path = os.path.relpath(filepath, root_dir)
    filename = os.path.basename(filepath)
    
    # Skip excluded files
    if filename in ["index.html", "404.html", "google123.html"]: # Add any other excludes
        return

    # Determine Language
    lang = "de" if "/de/" in rel_path or rel_path.startswith("de/") else "en"
    
    # Determine Hub
    hub_key = None
    if "blog-posts" in rel_path:
        hub_key = "blog"
    elif filename in COURSE_FILES:
        hub_key = "schedule"
    # Note: 'schedule.html' itself is a Hub, so it gets Level 2 (Home > Schedule). 
    # Logic below handles it: filename is 'schedule.html', not in COURSE_FILES, so Hub=None -> Home > Schedule. Perfect.

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract Title
    page_title = get_page_title(content)
    
    # 2. Generate New Schema
    # For the URL in schema, we need the web path, not file path
    # e.g. blog-posts/foo.html -> blog-posts/foo (clean URLs if implemented) or keep .html if not
    # User previously mentioned wanting clean URLs, but let's stick to current file structure for safety 
    # unless we know .html is stripped. Let's use the file name for now to be safe and match duplication check.
    # Actually, user wants clean URLs. Let's strip .html for the ITEM URL if it's internal.
    web_url_path = rel_path
    # Rule: user said "implementing clean URLs" in history. Let's strip .html for the canonical ID.
    if web_url_path.endswith(".html"):
        web_url_path = web_url_path[:-5]
    
    breadcrumb_data = generate_breadcrumb_json(lang, hub_key, page_title, web_url_path)
    breadcrumb_script = f'<script type="application/ld+json">\n    {json.dumps(breadcrumb_data, indent=4)}\n    </script>'

    # 3. Remove EXISTING BreadcrumbList blocks
    # Regex to match the entire script block containing "BreadcrumbList"
    # We use a non-greedy match for the content inside script tags
    # Pattern: <script type="application/ld+json"> ... "BreadcrumbList" ... </script>
    # flags=re.DOTALL to match newlines
    
    pattern = r'<script type="application/ld\+json">\s*\{[^}]*?"@type":\s*"BreadcrumbList"[^}]*?\}\s*</script>'
    # This specific regex might be too simple if there are nested braces, but JSON-LD usually isn't deeply nested for breadcrumbs.
    # A safer approach for JSON blocks is capturing the content and checking.
    
    # Robust Regex: Match <script...>...</script> then check content
    script_pattern = r'(<script type="application/ld\+json">)(.*?)(</script>)'
    
    def replacer(match):
        inner_content = match.group(2)
        if '"BreadcrumbList"' in inner_content:
            return "" # Remove it
        return match.group(0) # Keep it (e.g. Person, Course, FAQ)

    new_content = re.sub(script_pattern, replacer, content, flags=re.DOTALL)
    
    # 4. Inject New Schema
    # Insert before </head>
    if breadcrumb_script not in new_content: # Safety check
        if "</head>" in new_content:
            new_content = new_content.replace("</head>", f"{breadcrumb_script}\n</head>")
        else:
            print(f"[ERROR] No </head> tag in {rel_path}")
            return

    # Write back if changed
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[FIXED] {rel_path} -> Added Breadcrumb ({lang}, Hub={hub_key})")
    else:
        print(f"[SKIP] {rel_path} -> No changes needed")

def main():
    root_dir = os.getcwd()
    print("Starting Breadcrumb Injection...")
    
    for subdir, dirs, files in os.walk(root_dir):
        if ".git" in subdir or "node_modules" in subdir:
            continue
            
        for file in files:
            if file.endswith(".html"):
                process_file(os.path.join(subdir, file), root_dir)

    print("Injection Complete.")

if __name__ == "__main__":
    main()
