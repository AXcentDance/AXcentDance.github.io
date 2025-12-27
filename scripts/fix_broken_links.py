import os

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def fix_links():
    count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root or "System" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. Fix Login/Signup links (add underscore)
            # Handle both relative and root links
            content = content.replace('href="login"', 'href="_login"')
            content = content.replace('href="../login"', 'href="../_login"')
            
            content = content.replace('href="signup"', 'href="_signup"')
            content = content.replace('href="../signup"', 'href="../_signup"')
            
            # 2. Fix Collaborations (Missing file) -> Point to nothing or hide
            # Used in mobile drawer
            # <a href="../collaborations" class="drawer-link"><span>Collaborations</span></a>
            # We will comment it out or just make it dead but valid
            content = content.replace('href="../collaborations"', 'href="#" style="display:none;"')
            content = content.replace('href="collaborations"', 'href="#" style="display:none;"')
            
            # 3. Specific fixes for romeo-prince-collaboration-2025.html (and others if copied)
            # <li><a href="../">Terms & Conditions</a></li> -> href="../terms"
            # <li><a href="../pr">Privacy Policy</a></li> -> href="../privacy"
            # <li><a href="../im">Imprint</a></li> -> href="../imprint"
            
            if "blog-posts" in root:
                 content = content.replace('<li><a href="../">Terms & Conditions</a></li>', '<li><a href="../terms">Terms & Conditions</a></li>')
                 content = content.replace('href="../pr"', 'href="../privacy"')
                 content = content.replace('href="../im"', 'href="../imprint"')

            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed links in: {file}")
                count += 1
                
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    fix_links()
