import os
import subprocess

SRC = "assets/images/hero_new.webp"
SIZES = [480, 800, 1200]

def main():
    if not os.path.exists(SRC):
        print(f"File not found: {SRC}")
        return

    base, ext = os.path.splitext(SRC)
    
    for width in SIZES:
        dst = f"{base}_{width}w{ext}"
        print(f"Generating {dst}...")
        cmd = [
            'ffmpeg', '-i', SRC,
            '-vf', f'scale={width}:-1',
            '-c:v', 'libwebp', '-q:v', '75',
            dst, '-y'
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("Done.")

if __name__ == "__main__":
    main()
