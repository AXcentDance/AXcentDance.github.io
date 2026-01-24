import os
import re

def parse_master_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.findall(r'\| \*\*.*?\*\* \| `(.*?)` \| (.*?) \| (.*?) \|', content)
    master_data = {}
    for file, title, desc in matches:
        master_data[file.strip()] = {
            'title': title.strip(),
            'desc': desc.strip()
        }
    return master_data

def fix_german_page(file_path, master_data, rel_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Fix lang="de"
    content = re.sub(r'<html\s+lang=["\']en["\']', '<html lang="de"', content, flags=re.I)
    
    # 2. Get expected metadata
    search_key = os.path.basename(rel_path)
    if rel_path in master_data:
        expected = master_data[rel_path]
    elif search_key in master_data:
        expected = master_data[search_key]
    else:
        # No master data, but still fix lang
        if original_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed lang in (no master data): {rel_path}")
        return

    # 3. Apply Title
    expected_title = expected['title']
    content = re.sub(r'<title>.*?</title>', f'<title>{expected_title}</title>', content, flags=re.I|re.S)
    
    # 4. Apply Description
    expected_desc = expected['desc']
    
    # Improved meta description replacement
    def replace_desc(match):
        meta_tag = match.group(0)
        # Replace content within this tag
        return re.sub(r'content=(["\']).*?\1', f'content="{expected_desc}"', meta_tag, flags=re.I | re.S)

    meta_desc_regex = re.compile(r'<meta\s+[^>]*?name=["\']description["\'][^>]*?>', re.I | re.S)
    if meta_desc_regex.search(content):
        content = meta_desc_regex.sub(replace_desc, content)
    else:
        # try content first pattern
        meta_desc_regex_cf = re.compile(r'<meta\s+[^>]*?content=["\'].*?["\'][^>]*?name=["\']description["\'][^>]*?>', re.I | re.S)
        if meta_desc_regex_cf.search(content):
            content = meta_desc_regex_cf.sub(replace_desc, content)
        else:
            # Not found, insert after character set or title
            content = re.sub(r'(</title>)', rf'\1\n    <meta name="description" content="{expected_desc}">', content, flags=re.I)

    # 5. Fix OG Tags
    if 'og:title' in content:
        content = re.sub(r'(<meta\s+property=["\']og:title["\']\s+content=)(["\']).*?\2', rf'\1"{expected_title}"', content, flags=re.I | re.S)
    if 'og:description' in content:
        content = re.sub(r'(<meta\s+property=["\']og:description["\']\s+content=)(["\']).*?\2', rf'\1"{expected_desc}"', content, flags=re.I | re.S)
    if 'og:locale' in content:
        content = re.sub(r'(<meta\s+property=["\']og:locale["\']\s+content=)(["\']).*?\2', r'\1"de_CH"', content, flags=re.I | re.S)
    else:
        content = re.sub(r'(<meta name=["\']description["\'].*?>)', r'\1\n    <meta property="og:locale" content="de_CH">', content, flags=re.I | re.S)

    # 6. Hreflang Tags
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
    
    # Remove existing hreflang tags to avoid duplicates
    content = re.sub(r'\s*<link\s+rel=["\']alternate["\']\s+hreflang=.*?>', '', content, flags=re.I)
    
    # Insert new tags after canonical or viewport
    if '<link rel="canonical"' in content:
        content = re.sub(r'(<link rel=["\']canonical["\'].*?>)', rf'\1\n{hreflang_tags}', content, flags=re.I)
    else:
        content = re.sub(r'(<meta name=["\']viewport["\'].*?>)', rf'\1\n{hreflang_tags}', content, flags=re.I)

    # 7. Schema JSON-LD (same as before)
    schema_trans = {
        '"jobTitle": "Co-Founder"': '"jobTitle": "Mitbegründer"',
        '"jobTitle": "Founder & Dance Instructor"': '"jobTitle": "Gründer & Tanzlehrer"',
        '"name": "About Us"': '"name": "Über uns"',
        '"name": "Schedule"': '"name": "Stundenplan"',
        '"name": "Registration"': '"name": "Anmeldung"',
        '"name": "Contact"': '"name": "Kontakt"',
        '"name": "Home"': '"name": "Home"',
        '"name": "Education"': '"name": "Ausbildung"',
        '"name": "Bachata Guide"': '"name": "Bachata Guide"',
        '"name": "Book a Free Trial Class"': '"name": "Kostenlose Probelektion buchen"',
        '"name": "Education Hub"': '"name": "Ausbildungszentrum"',
        '"description": "Co-founder of AXcent Dance, international Bachata artist, and IDO Swiss Championship judge."': '"description": "Mitbegründer von AXcent Dance, internationaler Bachata-Künstler und Wertungsrichter der IDO Swiss Championship."',
        '"award":': '"award":',
        '"Judge at Swiss Championship"': '"Wertungsrichter bei der Schweizermeisterschaft"',
        '"Organizer of Bachata Congress"': '"Organisator des Bachata Kongresses"',
        '"International Bachata Dance Artist"': '"Internationaler Bachata-Tanzkünstler"',
    }
    for old, new in schema_trans.items():
        content = content.replace(old, new)

    if original_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed SEO, Hreflang & Schema in: {rel_path}")

def main():
    master_list_path = '/Users/slamitza/AXcentWebsiteGitHub/System/seo_metadata_master_list_de.md'
    de_root = '/Users/slamitza/AXcentWebsiteGitHub/de'
    master_data = parse_master_list(master_list_path)
    for root, dirs, files in os.walk(de_root):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, de_root)
                fix_german_page(file_path, master_data, rel_path)

if __name__ == "__main__":
    main()
