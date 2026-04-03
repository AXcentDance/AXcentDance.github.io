import os
import re
from datetime import datetime

def get_offset(date_str):
    """
    Returns the UTC offset string for a given YYYY-MM-DD date in Zurich.
    Summer time 2025: Mar 30 - Oct 26
    Summer time 2026: starts Mar 29
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 2025 Summer: Mar 30 to Oct 26
        summer_start_2025 = datetime(2025, 3, 30)
        summer_end_2025 = datetime(2025, 10, 26)
        
        # 2026 Summer: starts Mar 29
        summer_start_2026 = datetime(2026, 3, 29)
        
        if summer_start_2025 <= dt < summer_end_2025:
            return "+02:00"
        elif dt >= summer_start_2026:
            return "+02:00"
        else:
            return "+01:00"
    except ValueError:
        return "+01:00" # Default

def fix_dates_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern for JSON-LD datePublished and dateModified
    # Matches "datePublished": "2025-12-07"
    # Group 1: key (datePublished or dateModified)
    # Group 2: date string (YYYY-MM-DD)
    pattern = r'("(?:datePublished|dateModified)"\s*:\s*")(\d{4}-\d{2}-\d{2})(")'
    
    def replace_date(match):
        key_part = match.group(1)
        date_str = match.group(2)
        end_quote = match.group(3)
        
        offset = get_offset(date_str)
        new_value = f"{date_str}T12:00:00{offset}"
        return f"{key_part}{new_value}{end_quote}"

    new_content = re.sub(pattern, replace_date, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modified_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories to be fast
        if any(skip in root for skip in ['node_modules', '.git', '.agent', 'scripts', 'assets']):
            continue
            
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                if fix_dates_in_file(filepath):
                    modified_files.append(os.path.relpath(filepath, root_dir))
    
    if modified_files:
        print(f"Successfully updated {len(modified_files)} files:")
        for f in modified_files:
            print(f" - {f}")
    else:
        print("No files needed updating.")

if __name__ == "__main__":
    main()
