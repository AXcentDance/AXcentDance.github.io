from PIL import Image
import os

src = "assets/images/bachata_education_book.png"
dst = "assets/images/bachata_education_book.webp"

if os.path.exists(src):
    img = Image.open(src)
    img.save(dst, "WEBP", quality=85)
    print(f"Converted {src} to {dst}")
else:
    print(f"Source file {src} not found")
