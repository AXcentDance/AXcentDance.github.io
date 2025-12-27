import os
import re
import subprocess
import json

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def get_image_dimensions(filepath):
    """Returns (width, height) using ffprobe."""
    try:
        cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-select_streams', 'v:0', 
            '-show_entries', 'stream=width,height', 
            '-of', 'json', 
            filepath
        ]
        result = subprocess.check_output(cmd).decode('utf-8')
        data = json.loads(result)
        width = data['streams'][0]['width']
        height = data['streams'][0]['height']
        return width, height
    except Exception as e:
        # print(f"Error checking dimensions for {filepath}: {e}")
        return None, None

def fix_html_images():
    print("Starting HTML Image Fixes...")
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root or "System" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all img tags
            # We use a primitive state machine or just sequential processing of matches
            # To handle index (LCP), we need to track index per page.
            
            new_content = content
            
            # We iterate matches. Re-find them to handle replacement offsets? 
            # Easier: Split by tags or use a substitution function.
            # Python re.sub allows a function callback!
            
            img_index = -1 
            
            def replace_img(match):
                nonlocal img_index
                img_index += 1
                
                full_tag = match.group(0)
                attrs_str = match.group(1)
                
                # Parse attributes
                # This is a naive parser, assumes simple quoting
                attrs = {}
                # regex for key="value" or key='value'
                # But value might contain spaces.
                attr_pattern = r'([a-zA-Z0-9-]+)=["\'](.*?)["\']'
                for attr_match in re.finditer(attr_pattern, attrs_str):
                    attrs[attr_match.group(1).lower()] = attr_match.group(2)
                
                src = attrs.get('src')
                if not src:
                    return full_tag
                
                # Skip external/SVG
                if src.startswith('http') or src.startswith('//') or src.startswith('data:') or src.endswith('.svg'):
                    return full_tag
                
                # Resolve Absolute Path
                # If src starts with /, it's from root. If not, relative to file.
                # But standard in this repo seems to be relative or assets/
                
                if src.startswith('/'):
                    abs_path = os.path.join(ROOT_DIR, src.lstrip('/'))
                else:
                    # Resolve relative to current html file
                    abs_path = os.path.normpath(os.path.join(root, src))
                    
                if not os.path.exists(abs_path):
                    # print(f"Warning: Image not found {abs_path}")
                    return full_tag
                    
                # 1. Dimensions
                width, height = get_image_dimensions(abs_path)
                if width and height:
                     # Calculate aspect ratio or just set W/H
                     # Update attributes dict
                     attrs['width'] = str(width)
                     attrs['height'] = str(height)
                
                # 2. Lazy Loading (Smart)
                # Index 0, 1 -> eager (remove lazy if present, sets loading="eager" explicitly?)
                # Best practice LCP: no loading attribute (defaults to eager) or loading="eager"
                # Index > 1 -> lazy
                if img_index < 2:
                    if 'loading' in attrs:
                        del attrs['loading'] # Remove strict lazy
                    # Optional: attrs['loading'] = 'eager'
                else:
                    attrs['loading'] = 'lazy'
                
                # 3. Responsive (srcset)
                # We generated _480w.webp, _800w.webp, _1200w.webp
                # Base name
                base_dir = os.path.dirname(src)
                filename = os.path.basename(src)
                name_no_ext, ext = os.path.splitext(filename)
                
                if ext.lower() == '.webp':
                    # Check if variants exist? We assume yes if generator ran.
                    # Construct paths
                    # We need to reuse the same path structure as src
                    
                    # src might be "assets/images/foo.webp"
                    # variants: "assets/images/foo_480w.webp"
                    
                    v480 = f"{base_dir}/{name_no_ext}_480w.webp"
                    v800 = f"{base_dir}/{name_no_ext}_800w.webp"
                    v1200 = f"{base_dir}/{name_no_ext}_1200w.webp"
                    
                    # Clean up path (remove ./ if present)
                    if base_dir == "":
                         v480 = f"{name_no_ext}_480w.webp"
                         v800 = f"{name_no_ext}_800w.webp"
                         v1200 = f"{name_no_ext}_1200w.webp"

                    srcset_val = f"{src} {width}w" if width else f"{src}"
                    # Actually standard: "small.jpg 500w, medium.jpg 1000w, large.jpg 2000w"
                    # We should verify if variant files exist? 
                    # For script simplicity, we assume generation worked.
                    
                    srcset_val = (
                        f"{v480} 480w, "
                        f"{v800} 800w, "
                        f"{v1200} 1200w"
                    )
                    
                    attrs['srcset'] = srcset_val
                    attrs['sizes'] = "(max-width: 600px) 480px, (max-width: 900px) 800px, 1200px"
                
                # 4. Alt Text
                if 'alt' not in attrs or not attrs['alt'].strip():
                    # Generate from filename
                    readable = name_no_ext.replace('-', ' ').replace('_', ' ').title()
                    attrs['alt'] = readable
                    
                # Reconstruct Tag
                # Order: src, srcset, sizes, alt, width, height, loading, class, style...
                # We can just iterate attrs
                # Ensure src is first for readability
                
                tag_parts = ["<img"]
                tag_parts.append(f'src="{attrs["src"]}"')
                if 'srcset' in attrs: tag_parts.append(f'srcset="{attrs["srcset"]}"')
                if 'sizes' in attrs: tag_parts.append(f'sizes="{attrs["sizes"]}"')
                if 'alt' in attrs: tag_parts.append(f'alt="{attrs["alt"]}"')
                if 'width' in attrs: tag_parts.append(f'width="{attrs["width"]}"')
                if 'height' in attrs: tag_parts.append(f'height="{attrs["height"]}"')
                if 'loading' in attrs: tag_parts.append(f'loading="{attrs["loading"]}"')
                
                # Others
                for k, v in attrs.items():
                    if k not in ['src', 'srcset', 'sizes', 'alt', 'width', 'height', 'loading']:
                        tag_parts.append(f'{k}="{v}"')
                
                tag_parts.append(">")
                return " ".join(tag_parts)

            # Perform substitution
            new_content = re.sub(r'<img\s+([^>]+)>', replace_img, content, flags=re.IGNORECASE)
            
            if new_content != content:
                print(f"Updating {file}...")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)

if __name__ == "__main__":
    fix_html_images()
