import os
import re

def parse_master_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex to find table rows | **Name** | `file` | Title | Desc |
    matches = re.findall(r'\| \*\*.*?\*\* \| `(.*?)` \| (.*?) \| (.*?) \|', content)
    master_data = {}
    for file, title, desc in matches:
        master_data[file.strip()] = {
            'title': title.strip().replace('\\|', '|'),
            'desc': desc.strip().replace('\\|', '|')
        }
    return master_data

def audit_german_pages(de_root, master_data):
    results = []
    
    # Special case for blog posts which might be in de/blog-posts/
    for root, dirs, files in os.walk(de_root):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, de_root)
                
                # Normalize rel_path to match master list (mostly filename)
                # Master list uses 'index.html', 'about.html', etc.
                # but for blog posts it might use the relative path from de/
                search_key = rel_path
                if rel_path.startswith('blog-posts/'):
                    search_key = rel_path
                else:
                    search_key = os.path.basename(rel_path)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check lang="de" (flexible whitespace)
                has_lang_de = bool(re.search(r'<html\s+lang=["\']de["\']', content, re.I))
                
                # Extract Title (case insensitive, handle multi-line)
                title_match = re.search(r'<title>(.*?)</title>', content, re.I | re.S)
                curr_title = re.sub(r'\s+', ' ', title_match.group(1).strip()) if title_match else None
                
                # Extract Desc (flexible whitespace and quote-aware)
                desc_match = re.search(r'<meta\s+[^>]*?name=["\']description["\'][^>]*?content=(["\'])(.*?)\1', content, re.I | re.S)
                if not desc_match:
                    desc_match = re.search(r'<meta\s+[^>]*?content=(["\'])(.*?)\1[^>]*?name=["\']description["\']', content, re.I | re.S)
                
                curr_desc = re.sub(r'\s+', ' ', desc_match.group(2).strip()) if desc_match else None
                
                # Log issues
                issues = []
                if not has_lang_de:
                    issues.append("Missing lang=\"de\" or still in lang=\"en\"")
                
                # Matching Logic Improvement
                expected = None
                if rel_path in master_data:
                    expected = master_data[rel_path]
                elif os.path.basename(rel_path) in master_data:
                    expected = master_data[os.path.basename(rel_path)]
                
                if expected:
                    # Normalized comparison
                    norm_expected_title = re.sub(r'\s+', ' ', expected['title'])
                    if curr_title != norm_expected_title:
                        issues.append(f"Title mismatch. Expected: {norm_expected_title}, Found: {curr_title}")
                    
                    norm_expected_desc = re.sub(r'\s+', ' ', expected['desc'])
                    if curr_desc != norm_expected_desc:
                        issues.append(f"Desc mismatch. Expected: {norm_expected_desc}, Found: {curr_desc}")
                else:
                    issues.append(f"Not found in master list (tried {rel_path} and {os.path.basename(rel_path)})")
                
                if issues:
                    results.append({
                        'file': rel_path,
                        'issues': issues
                    })
    return results

def main():
    master_list_path = '/Users/slamitza/AXcentWebsiteGitHub/System/seo_metadata_master_list_de.md'
    de_root = '/Users/slamitza/AXcentWebsiteGitHub/de'
    
    master_data = parse_master_list(master_list_path)
    audit_results = audit_german_pages(de_root, master_data)
    
    if not audit_results:
        print("✅ No SEO issues found in German pages!")
    else:
        print(f"⚠️ Found {len(audit_results)} pages with issues:")
        for res in audit_results:
            print(f"\n[{res['file']}]")
            for issue in res['issues']:
                print(f"  - {issue}")

if __name__ == "__main__":
    main()
