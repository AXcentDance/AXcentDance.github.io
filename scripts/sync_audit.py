
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_sync():
    print("## AXcent Dance: Translation Sync Audit")
    print("Checking for missing German (DE) counterparts for English (EN) pages...")
    print("-" * 60)

    # Directories to check (relative to root)
    target_dirs = [
        "",             # Root
        "blog-posts"    # Blog Posts
    ]

    # Files to ignore (e.g., system files, auth pages that might be EN-only for now)
    ignore_files = {
        "admin.html",
        "_login.html",
        "_signup.html",
        "portal.html",
        "thank-you.html",
        "thank-you-contact.html",
        "thank-you-trial.html",
        "404.html"
    }

    missing_de = []
    
    for rel_dir in target_dirs:
        search_path = os.path.join(ROOT_DIR, rel_dir)
        
        if not os.path.exists(search_path):
            continue

        # List files in the directory
        for item in os.listdir(search_path):
            if not item.endswith(".html"):
                continue
            
            if item in ignore_files or item.startswith("."):
                continue

            # Full EN path
            en_path = os.path.join(rel_dir, item)
            
            # Expected DE path
            # Root files go to de/filename.html
            # blog-posts/file.html goes to de/blog-posts/file.html
            de_path = os.path.join("de", en_path)
            full_de_path = os.path.join(ROOT_DIR, de_path)

            if not os.path.exists(full_de_path):
                missing_de.append(en_path)

    if missing_de:
        print(f"FAILED: Found {len(missing_de)} English pages without a German translation:")
        for path in sorted(missing_de):
            print(f" [MISSING DE] -> {path}")
    else:
        print("SUCCESS: All English pages have a corresponding German translation.")

    print("-" * 60)
    
    # Reverse check: Are there German files that don't exist in English?
    print("\nChecking for orphaned German pages (DE without EN counterpart)...")
    orphaned_de = []
    
    de_root = os.path.join(ROOT_DIR, "de")
    if os.path.exists(de_root):
        for root, dirs, files in os.walk(de_root):
            for file in files:
                if not file.endswith(".html"):
                    continue
                
                # Get path relative to the 'de' directory
                full_path = os.path.join(root, file)
                rel_to_de = os.path.relpath(full_path, de_root)
                
                # Check if this exists in the root (EN)
                full_en_path = os.path.join(ROOT_DIR, rel_to_de)
                
                if not os.path.exists(full_en_path):
                    orphaned_de.append(os.path.join("de", rel_to_de))

    if orphaned_de:
        print(f"INFO: Found {len(orphaned_de)} German pages without an English counterpart:")
        for path in sorted(orphaned_de):
            print(f" [ORPHANED DE] -> {path}")
    else:
        print("SUCCESS: All German pages have an English counterpart.")

if __name__ == "__main__":
    check_sync()
