import os
import subprocess
import shutil

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"
ASSETS_DIR = os.path.join(ROOT_DIR, "assets", "images")

# Target widths
VARIANTS = [480, 800, 1200]

def generate_variants():
    count = 0
    skipped = 0
    errors = 0

    print("Starting responsive image generation...")
    print(f"Scanning directory: {ASSETS_DIR}")

    for root, dirs, files in os.walk(ASSETS_DIR):
        for file in files:
            if not file.lower().endswith(".webp"):
                continue
            
            # Skip existing variants
            if any(f"_{w}w.webp" in file for w in VARIANTS):
                continue

            src_path = os.path.join(root, file)
            base_name, _ = os.path.splitext(file)
            
            for width in VARIANTS:
                variant_name = f"{base_name}_{width}w.webp"
                variant_path = os.path.join(root, variant_name)
                
                # Check if exists
                if os.path.exists(variant_path):
                    # print(f"Skipping {variant_name} (exists)")
                    skipped += 1
                    continue
                
                # We simply force generation to satisfy the strict 3-size rule
                # ffmpeg -i input.webp -vf scale=480:-1 output_480w.webp
                
                try:
                    subprocess.check_call([
                        'ffmpeg', 
                        '-v', 'error',
                        '-i', src_path, 
                        '-vf', f'scale={width}:-1', 
                        '-y',  # Overwrite
                        variant_path
                    ])
                    print(f"Generated: {variant_name}")
                    count += 1
                except subprocess.CalledProcessError as e:
                    print(f"Error generating {variant_name}: {e}")
                    errors += 1
    
    print("-" * 50)
    print(f"Generation Complete.")
    print(f"Created: {count}")
    print(f"Skipped (Already existed): {skipped}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    generate_variants()
