
import os
import re

def audit_breadcrumbs(root_dir):
    print(f"Scanning {root_dir} for BreadcrumbList schema...\n")
    
    files_without_schema = []
    files_with_duplicates = []
    files_valid = 0
    
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(subdir, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Count occurrences of "BreadcrumbList"
                        count = content.count('"BreadcrumbList"')
                        
                        if count == 0:
                            files_without_schema.append(filepath)
                        elif count > 1:
                            files_with_duplicates.append((filepath, count))
                        else:
                            files_valid += 1
                            
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    print(f"Total Valid Files: {files_valid}")
    
    if files_with_duplicates:
        print("\n[WARNING] Files with DUPLICATE Breadcrumb Schema:")
        for f, c in files_with_duplicates:
            rel_path = os.path.relpath(f, root_dir)
            print(f" - {rel_path} ({c} times)")
            
    if files_without_schema:
        print("\n[INFO] Files MISSING Breadcrumb Schema:")
        for f in files_without_schema:
            rel_path = os.path.relpath(f, root_dir)
            print(f" - {rel_path}")

    if not files_without_schema and not files_with_duplicates:
        print("\n✅ All checked files have exactly 1 BreadcrumbList schema.")

if __name__ == "__main__":
    audit_breadcrumbs(os.getcwd())
