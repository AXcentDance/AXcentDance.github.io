
import os
import re
import json
import datetime

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

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
    """Returns file modification time in ISO 8601 format with Zurich offset."""
    timestamp = os.path.getmtime(filepath)
    dt = datetime.datetime.fromtimestamp(timestamp)
    date_str = dt.strftime('%Y-%m-%d')
    offset = get_offset(dt)
    return f"{date_str}T12:00:00{offset}"

def update_blog_dates(filepath):
    rel_path = os.path.relpath(filepath, ROOT_DIR)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lastmod = get_lastmod(filepath)
    
    # Pattern to find BlogPosting schema
    script_pattern = r'(<script type="application/ld\+json">)(.*?)(</script>)'
    
    def replacer(match):
        inner_content = match.group(2)
        if '"@type": "BlogPosting"' in inner_content or '"@type":"BlogPosting"' in inner_content:
            try:
                data = json.loads(inner_content)
                if data.get("@type") == "BlogPosting":
                    if data.get("dateModified") != lastmod:
                        data["dateModified"] = lastmod
                        # Return formatted JSON, preserving some aesthetic if possible
                        # but standard json.dumps is safest for well-formedness
                        new_json = json.dumps(data, indent=4)
                        return f'{match.group(1)}\n    {new_json}\n    {match.group(3)}'
            except Exception as e:
                print(f"Error parsing JSON in {rel_path}: {e}")
        return match.group(0)

    new_content = re.sub(script_pattern, replacer, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[UPDATED] {rel_path} -> dateModified set to {lastmod}")
    else:
        # print(f"[SKIP] {rel_path} -> Already up to date")
        pass

def main():
    print("Syncing Blog dateModified with file timestamps...")
    
    blog_dirs = [
        os.path.join(ROOT_DIR, 'blog-posts'),
        os.path.join(ROOT_DIR, 'de/blog-posts')
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
