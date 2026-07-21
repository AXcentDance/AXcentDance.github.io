
import os
import re
import json
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_offset(dt):
    """
    Returns the UTC offset string for a given date in Zurich.
    Summer time 2025: Mar 30 - Oct 26
    Summer time 2026: starts Mar 29
    """
    # 2025 Summer: Mar 30 to Oct 26
    summer_start_2025 = datetime.datetime(2025, 3, 30)
    summer_end_2025 = datetime.datetime(2025, 10, 26)
    
    # 2026 Summer: starts Mar 29
    summer_start_2026 = datetime.datetime(2026, 3, 29)
    
    if summer_start_2025 <= dt < summer_end_2025:
        return "+02:00"
    elif dt >= summer_start_2026:
        return "+02:00"
    else:
        return "+01:00"

def get_lastmod(filepath):
    """Returns file modification date (date-only ISO 8601, site convention for dateModified)."""
    timestamp = os.path.getmtime(filepath)
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d')

def update_blog_dates(filepath):
    rel_path = os.path.relpath(filepath, ROOT_DIR)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lastmod = get_lastmod(filepath)

    # Only touch pages that carry a BlogPosting node (live posts use a @graph)
    if '"@type": "BlogPosting"' not in content and '"@type":"BlogPosting"' not in content:
        return

    # Replace the dateModified value in place; keeps the hand-formatted @graph intact
    new_content, n = re.subn(
        r'("dateModified":\s*")[^"]*(")',
        lambda m: m.group(1) + lastmod + m.group(2),
        content,
    )

    if n and new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[UPDATED] {rel_path} -> dateModified set to {lastmod}")

def main():
    print("Syncing Blog dateModified with file timestamps...")

    blog_dirs = [
        os.path.join(ROOT_DIR, 'blog'),
        os.path.join(ROOT_DIR, 'de/blog')
    ]
    
    for blog_dir in blog_dirs:
        if not os.path.exists(blog_dir):
            continue
            
        for file in os.listdir(blog_dir):
            if file.endswith(".html"):
                update_blog_dates(os.path.join(blog_dir, file))

    print("Sync Complete.")

if __name__ == "__main__":
    main()
