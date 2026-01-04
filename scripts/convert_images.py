import os
import subprocess

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

# List of images to optimize (relative to repo root)
IMAGES_TO_CONVERT = [
    "assets/images/hero_new.jpg"
]

def convert_and_update():
    for img_rel_path in IMAGES_TO_CONVERT:
        src_path = os.path.join(ROOT_DIR, img_rel_path)
        
        if not os.path.exists(src_path):
            print(f"Skipping missing file: {img_rel_path}")
            continue
            
        # Determine new path
        # Split ext
        base, ext = os.path.splitext(src_path)
        dst_path = base + ".webp"
        
        # 1. Convert using ffmpeg
        print(f"Converting: {img_rel_path} -> .webp")
        try:
            # ffmpeg -i input -c:v libwebp -q:v 75 output.webp
            subprocess.check_call(['ffmpeg', '-i', src_path, '-c:v', 'libwebp', '-q:v', '75', dst_path, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {img_rel_path}: {e}")
            continue
            
        # 2. Update references in HTML files
        # We need to replace 'filename.png' with 'filename.webp' in all HTML files
        # We use the basename to be safe across relative paths
        
        filename_ext = os.path.basename(src_path)     # e.g. dance-tips-1-title.png
        filename_new = os.path.basename(dst_path)     # e.g. dance-tips-1-title.webp
        
        print(f"Updating references: {filename_ext} -> {filename_new}")
        
        update_html_references(filename_ext, filename_new)
        
        # Optional: Delete original if verify?
        # os.remove(src_path) 
        # Keeping original for now to be safe.

def update_html_references(old_name, new_name):
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root:
            continue
        
        for file in files:
            if not file.endswith(".html"):
                continue
                
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_name in content:
                # Replace
                new_content = content.replace(old_name, new_name)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
    
    print(f"Updated {count} files for {old_name}")

if __name__ == "__main__":
    convert_and_update()
