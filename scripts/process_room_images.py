
import os
import sys
from PIL import Image

def process_image(input_path, output_name, dest_dir):
    try:
        img = Image.open(input_path)
        
        # Convert to RGB if necessary (e.g. for PNGs with transparency if saving as JPEG, but for WebP it handles alpha)
        # For consistency with the site style (photos), usually we want robust conversions.
        if img.mode == 'RGBA':
            # Keep alpha for WebP
            pass
        elif img.mode == 'P':
             img = img.convert('RGBA')

        base_name = os.path.join(dest_dir, output_name)
        
        # Define sizes
        sizes = {
            '1200w': 1200,
            '800w': 800,
            '480w': 480
        }
        
        # Save original size (or max 1920w) as base
        max_width = 1920
        if img.width > max_width:
             w_percent = (max_width / float(img.width))
             h_size = int((float(img.height) * float(w_percent)))
             img_resized = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
             img_resized.save(f"{base_name}.webp", "WEBP", quality=90)
        else:
             img.save(f"{base_name}.webp", "WEBP", quality=90)
             
        print(f"Saved base image: {base_name}.webp")

        # Generate variants
        for suffix, width in sizes.items():
            if img.width > width:
                w_percent = (width / float(img.width))
                h_size = int((float(img.height) * float(w_percent)))
                img_resized = img.resize((width, h_size), Image.Resampling.LANCZOS)
                img_resized.save(f"{base_name}_{suffix}.webp", "WEBP", quality=85)
                print(f"Saved variant: {base_name}_{suffix}.webp")
            else:
                # If original is smaller, just copy/save it as the variant name to avoid errors in srcset
                # or just don't create it? 
                # Better to have the file existing for srcset logic usually.
                img.save(f"{base_name}_{suffix}.webp", "WEBP", quality=85)
                print(f"Saved (upscaled/copy) variant: {base_name}_{suffix}.webp")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    # Image 1
    input1 = "/Users/slamitza/.gemini/antigravity/brain/f90524b2-cf56-4a62-903e-85b1bcf32eb7/uploaded_image_0_1769500306415.jpg"
    dest = "/Users/slamitza/AXcentWebsiteGitHub/assets/images/studio"
    process_image(input1, "studio_room_view_1", dest)

    # Image 2
    input2 = "/Users/slamitza/.gemini/antigravity/brain/f90524b2-cf56-4a62-903e-85b1bcf32eb7/uploaded_image_1_1769500306415.png"
    process_image(input2, "studio_room_view_2", dest)
