import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

MAPPING = {
    "class-bachata-beginner-0.html": "bachata-beginner-0.html",
    "class-bachata-beginner-2.html": "bachata-beginner-2.html",
    "class-bachata-sensual-foundation.html": "bachata-sensual-foundation.html",
    "class-bachata-sensual-improver.html": "bachata-sensual-improver.html",
    "class-bachata-sensual-inter-adv.html": "bachata-sensual-inter-adv.html",
    "class-lady-styling.html": "lady-styling.html"
}

def rename_files():
    print("Step 1: Renaming Files...")
    for old_name, new_name in MAPPING.items():
        old_path = os.path.join(ROOT_DIR, old_name)
        new_path = os.path.join(ROOT_DIR, new_name)
        
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed: {old_name} -> {new_name}")
        elif os.path.exists(new_path):
            print(f"Skipped: {new_name} already exists.")
        else:
            print(f"Error: {old_name} not found.")

def update_content():
    print("\nStep 2: Updating Content (Links & Canonicals)...")
    
    # We need to replace strings like:
    # "class-bachata-beginner-0.html" -> "bachata-beginner-0.html"
    # "class-bachata-beginner-0" -> "bachata-beginner-0" (for clean URLs if used)
    # Canonical: href="https://axcentdance.com/class-bachata-beginner-0"
    
    count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root or "System" in root:
            continue
            
        for file in files:
            # Update HTML, XML, JSON, JS, CSS? mostly HTML and XML
            if not (file.endswith(".html") or file.endswith(".xml") or file.endswith(".json")):
                continue
                
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            for old_name, new_name in MAPPING.items():
                # 1. Replace mapped filenames directly (e.g. href="class-bachata.html")
                new_content = new_content.replace(old_name, new_name)
                
                # 2. Replace clean URLs (without .html)
                old_clean = old_name.replace(".html", "")
                new_clean = new_name.replace(".html", "")
                
                # We replace instances of old_clean that are likely part of a URL
                # but NOT if they are part of a longer string that wasn't mapped?
                # Actually, given the specificity of these names, global replace is likely safe.
                # But let's be careful about double replacement if we run twice? No, old != new.
                
                # To avoid partial matches (e.g. class-bachata-beginner-0-ver2), we look for boundaries if possible
                # But simple replace is usually robust enough for these distinct slugs.
                
                new_content = new_content.replace(old_clean, new_clean)
            
            if new_content != content:
                print(f"Updated references in: {file}")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    rename_files()
    update_content()
