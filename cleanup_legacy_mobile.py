import os
import glob
import re

def cleanup_legacy_code():
    files = glob.glob("*.html")
    count = 0
    
    # Regex to capture the block. 
    # Starts with the big comment line
    # Ends with the closing style tag or similar, but looking at the file it seems to be at the bottom.
    # We will look for the specific marker and remove everything until the next major block or specific end pattern.
    # In the file view, it starts at line ~1279:
    # <!-- ==============================================
    # MOBILE DRAWER NAVIGATION (ISOLATED V6)
    # ============================================== -->
    # And contains <style>...</style>
    
    # We'll use a fairly aggressive regex to match this specific block structure
    start_marker = r'<!-- =+[\s\n]+MOBILE DRAWER NAVIGATION \(ISOLATED V6\)[\s\n]+=+\s-->.*?'
    # It ends with </style> usually for this block
    end_marker = r'<\/style>'
    
    pattern = re.compile(start_marker + end_marker, re.DOTALL | re.MULTILINE)

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if legacy code exists
            if "MOBILE DRAWER NAVIGATION (ISOLATED V6)" in content:
                # Remove it
                new_content = re.sub(pattern, '', content)
                
                # Double check if simple string replacement is safer if regex fails
                # The text is quite specific, maybe splittting is safer?
                # Let's try splitting if regex didn't change anything (or to be more robust)
                
                if new_content == content:
                   # Fallback: Split by the unique comment start
                   parts = content.split('<!-- ==============================================\n       MOBILE DRAWER NAVIGATION (ISOLATED V6)')
                   if len(parts) > 1:
                       # We found it. Now find where it ends. It usually ends with </style>
                       pre_part = parts[0]
                       rest = parts[1]
                       if '</style>' in rest:
                           post_part = rest.split('</style>', 1)[1]
                           new_content = pre_part + post_part
                
                # Update cache buster to complete the fix
                new_content = re.sub(r'style\.css\?v=mobilefix\d+', 'style.css?v=mobilefix14', new_content)

                if new_content != content:
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Cleaned {file}")
                    count += 1
                else:
                    print(f"Detected marker in {file} but failed to remove it.")
            else:
                # Just update cache buster even if no legacy code (uniformity)
                # Actually, only update if we change something? No, let's keep versions in sync
                new_content = re.sub(r'style\.css\?v=mobilefix\d+', 'style.css?v=mobilefix14', content)
                if new_content != content:
                     with open(file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                     # print(f"Updated cache buster in {file}")

        except Exception as e:
            print(f"Error processing {file}: {e}")

    print(f"Cleaned legacy code from {count} files.")

if __name__ == "__main__":
    cleanup_legacy_code()
