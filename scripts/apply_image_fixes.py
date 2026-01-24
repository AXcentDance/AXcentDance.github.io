import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"
DE_DIR = os.path.join(ROOT_DIR, "de")

def fix_srcset_paths():
    for root, dirs, files in os.walk(DE_DIR):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                # Determine relative depth for prefix
                # de/*.html -> ../
                # de/blog-posts/*.html -> ../../
                rel_path = os.path.relpath(filepath, ROOT_DIR)
                # "de/index.html" -> depth 1 -> need "../"
                # "de/blog-posts/post.html" -> depth 2 -> need "../../"
                depth = rel_path.count(os.sep) 
                
                if depth == 1:
                     prefix = "../"
                elif depth == 2:
                     prefix = "../../"
                else:
                     # fallback or deeper nesting
                     prefix = "../" * depth

                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                def replace_srcset(match):
                    attr_content = match.group(1)
                    sources = attr_content.split(',')
                    new_sources = []
                    for src in sources:
                        src = src.strip()
                        parts = src.split(' ') # split url and width/descriptor
                        url = parts[0]
                        rest = ' '.join(parts[1:])
                        
                        if url.startswith("assets/"):
                            new_url = f"{prefix}{url}"
                            if rest:
                                new_sources.append(f"{new_url} {rest}")
                            else:
                                new_sources.append(new_url)
                        else:
                            new_sources.append(src)
                    
                    return f'srcset="{", ".join(new_sources)}"'

                new_content = re.sub(r'srcset="([^"]*)"', replace_srcset, content)
                
                if new_content != content:
                    print(f"Fixed {rel_path}")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)

if __name__ == "__main__":
    fix_srcset_paths()
