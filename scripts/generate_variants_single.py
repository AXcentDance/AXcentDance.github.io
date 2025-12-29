import subprocess
import os
import sys

SIZES = [480, 800, 1200]

def scale_image(src, width):
    base, ext = os.path.splitext(src)
    # Output always webp
    dst = f"{base}_{width}w.webp"
    
    # If source is not webp, we might want a base webp too?
    # For now, just generating responsive variants.
    # Actually, let's also ensure a base webp exists if the source is jpg/png
    
    cmd = ["ffmpeg", "-i", src, "-vf", f"scale={width}:-1", "-c:v", "libwebp", "-q:v", "80", dst, "-y"]
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        print(f"Generated {dst}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate {dst}: {e}")

def convert_to_base_webp(src):
    base, ext = os.path.splitext(src)
    if ext.lower() == ".webp":
        return src
    
    dst = f"{base}.webp"
    cmd = ["ffmpeg", "-i", src, "-c:v", "libwebp", "-q:v", "80", dst, "-y"]
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        print(f"Generated base WebP: {dst}")
        return dst
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate base WebP {dst}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_variants_single.py <path_to_image>")
        sys.exit(1)
        
    source_file = sys.argv[1]
    
    if os.path.exists(source_file):
        # 1. Convert to base WebP if needed
        webp_source = convert_to_base_webp(source_file)
        
        # 2. Generate variants (using the original source to avoid double compression artifacts if possible, 
        # but using the path logic to name them correctly)
        # We will name them matchng the input filename base.
        
        for size in SIZES:
            scale_image(source_file, size)
    else:
        print(f"Source {source_file} not found")
