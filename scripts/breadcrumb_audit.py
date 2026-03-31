import os
import json
import re
from bs4 import BeautifulSoup

def audit_breadcrumbs(root_dir):
    print(f"--- Breadcrumb Deep Audit [Cortex-v3] ---\n")
    print(f"Scanning {root_dir}...")
    
    issues = []
    valid_files = 0
    total_files = 0
    
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".html"):
                continue
            
            total_files += 1
            filepath = os.path.join(subdir, file)
            rel_path = os.path.relpath(filepath, root_dir)
            
            # Skip root index/404
            if rel_path in ["index.html", "404.html", "de/index.html", "de/404.html"]:
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Find and check canonical
                    canonical_tag = soup.find('link', rel='canonical')
                    canonical_url = canonical_tag.get('href') if canonical_tag else None

                    # Find all JSON-LD scripts
                    scripts = soup.find_all('script', type='application/ld+json')
                    breadcrumb_found = False
                    
                    for script in scripts:
                        if not script.string: continue
                        try:
                            data = json.loads(script.string)
                            items = data.get('@graph', [data])
                            
                            for item in items:
                                if item.get('@type') == 'BreadcrumbList':
                                    breadcrumb_found = True
                                    res = validate_breadcrumb(item, rel_path, canonical_url)
                                    if res:
                                        issues.append((rel_path, res))
                                    else:
                                        valid_files += 1
                                    break
                                    
                        except json.JSONDecodeError:
                            issues.append((rel_path, ["Invalid JSON in <script> tag"]))
                    
                    if not breadcrumb_found:
                        issues.append((rel_path, ["Missing BreadcrumbList schema"]))
                        
            except Exception as e:
                issues.append((rel_path, [f"Error processing file: {e}"]))

    # Report results
    print(f"\nAudit complete.")
    print(f"Total HTML files analyzed: {total_files}")
    print(f"Files with Perfect Breadcrumbs: {valid_files}")
    print(f"Files with Issues: {len(issues)}")
    
    if issues:
        print("\n--- DETAILED ISSUES ---")
        for file, file_issues in sorted(issues):
            print(f"\n[FILE] {file}")
            for msg in file_issues:
                print(f"  - {msg}")

def validate_breadcrumb(schema, rel_path, canonical_url):
    errs = []
    elements = schema.get('itemListElement', [])
    is_german = rel_path.startswith("de/")
    
    if not elements:
        return ["BreadcrumbList has no itemListElement content"]
        
    # 1. Depth check
    if "blog-posts/" in rel_path:
        if len(elements) < 3:
            errs.append(f"Insufficient levels. Expected 3 (Home > Blog > Post), found {len(elements)}")
    elif len(elements) < 2:
        errs.append(f"Insufficient levels. Expected at least 2, found {len(elements)}")

    # 2. Level Content Check
    for i, el in enumerate(elements):
        pos = el.get('position')
        if pos != i + 1:
            errs.append(f"Invalid position at element {i}. Found {pos}, expected {i+1}")
        
        item = el.get('item', {})
        url = item if isinstance(item, str) else item.get('@id') or item.get('url')
        name = el.get('name') or item.get('name')
        
        if not url:
            errs.append(f"Missing URL for element at position {i+1}")
            continue
            
        # Absolute URL check
        if not url.startswith("http"):
            errs.append(f"Absolute URL required: '{url}' at position {i+1}")

        # Language parity check
        if is_german:
            if "https://axcentdance.com/" in url and "https://axcentdance.com/de/" not in url:
                # Home is exceptional (sometimes links to root), but parents should be localized
                if i > 0: # Not the first element
                    errs.append(f"Language mismatch: '{url}' in German page (missing /de/)")
        else:
            if "https://axcentdance.com/de/" in url:
                errs.append(f"Language mismatch: '{url}' in English page (contains /de/)")

        # Clean URL check
        if ".html" in url:
            errs.append(f"Clean URL violation: contains '.html' in '{url}'")
        if url.endswith("/"):
            # Home is exception, but others shouldn't have trailing slash if it's AXcent style
            if url != "https://axcentdance.com/" and url != "https://axcentdance.com/de/":
                errs.append(f"Trailing slash violation: '{url}'")

    # 3. Last Element Matching
    last_el = elements[-1]
    item_last = last_el.get('item', {})
    url_last = item_last if isinstance(item_last, str) else item_last.get('@id') or item_last.get('url')
    
    if canonical_url and url_last != canonical_url:
        errs.append(f"Last breadcrumb URL ({url_last}) does not match canonical ({canonical_url})")

    return errs

if __name__ == "__main__":
    audit_breadcrumbs(os.getcwd())
