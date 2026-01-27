#!/bin/bash

DEST="/Users/slamitza/AXcentWebsiteGitHub/assets/images/studio"
INPUT1="/Users/slamitza/.gemini/antigravity/brain/f90524b2-cf56-4a62-903e-85b1bcf32eb7/uploaded_image_0_1769500306415.jpg"
INPUT2="/Users/slamitza/.gemini/antigravity/brain/f90524b2-cf56-4a62-903e-85b1bcf32eb7/uploaded_image_1_1769500306415.png"

mkdir -p "$DEST"

# Function to process image
process() {
    local input="$1"
    local name="$2"
    local ext="$3" # fallback extension if webp fails

    echo "Processing $name..."

    # Try WebP
    if sips -s format webp "$input" --out "$DEST/$name.webp"; then
        echo "WebP conversion successful."
        sips -Z 1200 -s format webp "$input" --out "$DEST/${name}_1200w.webp"
        sips -Z 800 -s format webp "$input" --out "$DEST/${name}_800w.webp"
        sips -Z 480 -s format webp "$input" --out "$DEST/${name}_480w.webp"
    else
        echo "WebP not supported by sips. Fallback to original format."
        # Fallback to original format but resized
        cp "$input" "$DEST/$name.$ext"
        sips -Z 1200 "$input" --out "$DEST/${name}_1200w.$ext"
        sips -Z 800 "$input" --out "$DEST/${name}_800w.$ext"
        sips -Z 480 "$input" --out "$DEST/${name}_480w.$ext"
    fi
}

process "$INPUT1" "studio_room_view_1" "jpg"
process "$INPUT2" "studio_room_view_2" "png"
