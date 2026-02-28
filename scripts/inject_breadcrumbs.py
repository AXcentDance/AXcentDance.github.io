import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine language
    lang = "de" if "/de/" in file_path else "en"
    
    # Extract Title (stripped of site name)
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if not title_match:
        return
    
    title = title_match.group(1).split('|')[0].strip()
    
    # Prepare Visual Breadcrumb based on language
    if lang == "de":
        home_label = "Startseite"
        blog_label = "Blog"
        home_url = "../../"
        blog_url = "../../blog"
    else:
        home_label = "Home"
        blog_label = "Blog"
        home_url = "../"
        blog_url = "../blog"

    breadcrumb_html = f"""                <!-- Visual Breadcrumb -->
                <nav class="breadcrumb-nav" aria-label="Breadcrumb">
                    <ul class="breadcrumb-list">
                        <li><a href="{home_url}">{home_label}</a> <span class="separator">/</span></li>
                        <li><a href="{blog_url}">{blog_label}</a> <span class="separator">/</span></li>
                        <li aria-current="page">{title}</li>
                    </ul>
                </nav>"""

    # Check if breadcrumb-nav already exists
    if 'class="breadcrumb-nav"' in content:
        print(f"Skipping {file_path} - already has breadcrumb-nav")
        return

    # Find hero-content-z and insert at the top
    insertion_point = re.search(r'<div class="[^"]*hero-content-z[^"]*">', content, re.IGNORECASE)
    if not insertion_point:
        # Fallback to post-header
        insertion_point = re.search(r'<div class="[^"]*post-header[^"]*">', content, re.IGNORECASE)

    if insertion_point:
        pos = insertion_point.end()
        new_content = content[:pos] + "\n" + breadcrumb_html + content[pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
    else:
        print(f"COULD NOT FIND Insertion point in {file_path}")

# Find all blog posts
files_to_process = []
for root, dirs, files in os.walk(ROOT_DIR):
    if "blog-posts" in root:
        for f in files:
            if f.endswith(".html"):
                files_to_process.append(os.path.join(root, f))

for f in files_to_process:
    process_file(f)
