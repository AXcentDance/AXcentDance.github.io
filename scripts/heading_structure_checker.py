import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def check_headings():
    print(f"{'File':<40} | {'Status':<10} | {'Message'}")
    print("-" * 100)
    
    files_with_issues = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, ROOT_DIR)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all headings in order
            # This simple regex might miss nested tags inside h tags, but usually works for scanning
            headings = re.findall(r'<(h[1-6])', content, re.IGNORECASE)
            
            h1_count = headings.count('h1')
            issues = []
            
            # Check 1: Exactly one H1
            if h1_count == 0:
                issues.append("Missing H1")
            elif h1_count > 1:
                issues.append(f"Multiple H1s ({h1_count})")
                
            # Check 2: Hierarchy
            # Convert to integers
            levels = [int(h[1]) for h in headings]
            
            if levels:
                # Check first heading is usually h1 (not strict req, but good practice)
                if levels[0] != 1:
                    issues.append(f"Starts with H{levels[0]} (expected H1)")
                
                # Check skips
                for i in range(len(levels) - 1):
                    current = levels[i]
                    next_h = levels[i+1]
                    
                    # Going down (1 -> 2) is fine.
                    # Going UP (3 -> 2) is fine.
                    # Skipping levels down (1 -> 3) is bad.
                    if next_h > current + 1:
                        issues.append(f"Skipped level: H{current} -> H{next_h}")
                        
            if issues:
                print(f"{rel_path:<40} | WARN       | {'; '.join(issues)}")
                files_with_issues += 1
            else:
                # print(f"{rel_path:<40} | OK         |")
                pass

    print("-" * 100)
    print(f"Files with layout structure issues: {files_with_issues}")

if __name__ == "__main__":
    check_headings()
