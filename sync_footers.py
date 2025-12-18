import os
import glob
import re

def sync_footers():
    source_file = 'index.html'
    target_pattern = 'class-*.html' # Targeting course pages
    
    # 1. Read Source Footer
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract footer using regex
        footer_match = re.search(r'(<footer class="main-footer">.*?</footer>)', content, re.DOTALL)
        if not footer_match:
            print(f"Error: Could not find footer in {source_file}")
            return
            
        footer_html = footer_match.group(1)
        print(f"Extracted footer from {source_file} ({len(footer_html)} chars)")
        
    except Exception as e:
        print(f"Error reading source: {e}")
        return

    # 2. Update Targets
    targets = glob.glob(target_pattern) + glob.glob('guide-*.html') + ['private-lessons.html', 'education.html', 'room-rental.html', 'collaborations.html', 'corporate-events.html', 'wedding-dance.html', 'gallery.html', 'faq.html', 'etiquette.html']
    
    count = 0
    for file_path in targets:
        if file_path == source_file:
            continue
            
        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                target_content = f.read()
            
            # Check if target has a footer
            if '<footer class="main-footer">' not in target_content:
                print(f"Skipping {file_path}: No footer found to replace")
                continue
                
            # Replace footer
            new_content = re.sub(
                r'<footer class="main-footer">.*?</footer>', 
                footer_html, 
                target_content, 
                flags=re.DOTALL
            )
            
            if new_content != target_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated footer in {file_path}")
                count += 1
            else:
                print(f"No changes needed for {file_path}")
                
        except Exception as e:
            print(f"Error updating {file_path}: {e}")

    print(f"\nSuccessfully updated {count} files.")

if __name__ == "__main__":
    sync_footers()
