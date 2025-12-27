
from PIL import Image
import os

images = [
    "assets/images/blog/dance-tips-1-intro.png",
    "assets/images/blog/dance-tips-1-title.png",
    "assets/images/blog/dance-tips-1-good-frame.png",
    "assets/images/blog/dance-tips-1-bad-frame.png"
]

for img_path in images:
    if os.path.exists(img_path):
        try:
            with Image.open(img_path) as im:
                webp_path = img_path.replace(".png", ".webp")
                im.save(webp_path, "WEBP", quality=80)
                print(f"Converted {img_path} to {webp_path}")
                os.remove(img_path) # Clean up png
        except Exception as e:
            print(f"Error converting {img_path}: {e}")
    else:
        print(f"File not found: {img_path}")
