import subprocess
import os

SOURCE = "assets/images/faq_artistic_motion.webp"
SIZES = [480, 800, 1200]

def scale_image(src, width):
    base, ext = os.path.splitext(src)
    dst = f"{base}_{width}w{ext}"
    cmd = ["ffmpeg", "-i", src, "-vf", f"scale={width}:-1", "-c:v", "libwebp", "-q:v", "80", dst, "-y"]
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        print(f"Generated {dst}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate {dst}: {e}")

if os.path.exists(SOURCE):
    for size in SIZES:
        scale_image(SOURCE, size)
else:
    print(f"Source {SOURCE} not found")
