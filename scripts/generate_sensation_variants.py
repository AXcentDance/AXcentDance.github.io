from PIL import Image
import os

def resize_and_save(src_path, widths):
    if not os.path.exists(src_path):
        print(f"Source {src_path} not found.")
        return
    
    with Image.open(src_path) as img:
        base, ext = os.path.splitext(src_path)
        for w in widths:
            # Maintain aspect ratio
            h = int((float(img.size[1]) * float(w)) / float(img.size[0]))
            resized = img.resize((w, h), Image.Resampling.LANCZOS)
            dst_path = f"{base}_{w}w{ext}"
            resized.save(dst_path, "WEBP", quality=85)
            print(f"Generated {dst_path}")

# Sensation Blog Images
images = [
    "assets/images/blog/sensation-hero.webp",
    "assets/images/blog/sensation-body1.webp"
]

target_widths = [480, 800, 1200]

for img_path in images:
    resize_and_save(img_path, target_widths)
