import os
import re

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def fix_headings():
    count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in root or "node_modules" in root or "scripts" in root or "System" in root:
            continue
            
        for file in files:
            if not file.endswith(".html"):
                continue
                
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. Global Footer Fix: <h4 class="footer-heading"> -> <h2 class="footer-heading">
            # We use regex to capture the content and ensure we match the closing tag
            # Pattern: <h4 class="footer-heading">(.*?)</h4>
            # We replace with <h2 class="footer-heading">\1</h2>
            
            # Note: Regex improved to handle extra attributes like inline styles
            # Match <h4 ... class="footer-heading" ... > ... </h4>
            # We will just replace the "h4" with "h2" in the opening and closing tags if it contains the class
            
            # Simple approach: Find h4 with class footer-heading, capture attributes and content
            # pattern = r'<h4([^>]*)class="footer-heading"([^>]*)>(.*?)</h4>'
            # replacement = r'<h2\1class="footer-heading"\2>\3</h2>'
            # But the class ordering might vary.
            
            # Robust specific replacement for the known codebase:
            # We see cases like: <h4 class="footer-heading"> and <h4 class="footer-heading" style="...">
            
            content = re.sub(r'<h4 class="footer-heading"(.*?)>(.*?)</h4>', r'<h2 class="footer-heading"\1>\2</h2>', content)
            
            # 2. Admin.html Fixes
            if file == "admin.html":
                # Fix the stat card H1 (Count) -> use div with same style
                # <h1 id="checkInCount" style="font-size: 3rem; color: var(--accent-start);">0</h1>
                content = content.replace('<h1 id="checkInCount"', '<div id="checkInCount"')
                content = content.replace('">0</h1>', '">0</div>') # Closing tag for that specific line structure
                # Make sure to handle if 0 changes or if regex is safer
                # Regex for the ID
                content = re.sub(r'<h1 id="checkInCount"(.*?)>(.*?)</h1>', r'<div id="checkInCount"\1>\2</div>', content)
            
            # 3. Terms.html Fixes (Multiple H1s)
            if file == "terms.html":
                # Demote the second H1 (usually inside legal-content)
                # Matches <h1>...</h1> inside body if needed, but simple replacement of generic h1 might be risky if we have hero h1.
                # Hero H1 usually has a class or different context.
                # In terms.html, line 64 css targets ".legal-content h1".
                # Let's target <h1> inside legal content area if possible, or just all generic <h1> without class?
                # Actually, the Hero H1 usually has class="page-title" or similar.
                # The content H1 probably has no class.
                content = re.sub(r'<h1>', r'<h2>', content)
                content = re.sub(r'</h1>', r'</h2>', content)
                # But wait, we want to KEEP the hero H1.
                # Hero H1 in terms.html uses <h1 class="page-title">...</h1>
                # The other H1 might be <h1 style="..."> or just <h1>.
                # Let's revert the Hero H1 back to H1 after global replace? No, safer to target only non-class H1?
                # Regex: <h1(?![^>]*class=)[^>]*> matches H1 without class.
                content = re.sub(r'<h1(?![^>]*class=)([^>]*)>(.*?)</h1>', r'<h2\1>\2</h2>', content)

            # 4. Global Class Name upgrade (H4 -> H3) for Schedule/Index
            # Pattern: <h4 class="class-name"> -> <h3 class="class-name">
            content = re.sub(r'<h4 class="class-name"(.*?)>(.*?)</h4>', r'<h3 class="class-name"\1>\2</h3>', content)

            # 5. Admin.html Javascript String Fix (H1 -> H2 to avoid multiple H1s)
            if file == "admin.html":
                 # document.body.innerHTML = '...<h1>Access Denied 🚫</h1>...';
                 content = content.replace('<h1>Access Denied 🚫</h1>', '<h2>Access Denied 🚫</h2>')

            # 6. About.html and others: Promote "organizer-event-title" H3 -> H2
            # Also "Our Global Footprint" and "Our Philosophy" which are H3
            if file == "about.html" or file == "corporate-events.html":
                content = content.replace('<h3 class="organizer-event-title">', '<h2 class="organizer-event-title">')
                # Needs to match closing tag? No, generic H3 replace is dangerous.
                # Regex replace for specific class
                content = re.sub(r'<h3 class="organizer-event-title"(.*?)>(.*?)</h3>', r'<h2 class="organizer-event-title"\1>\2</h2>', content)
                
                # Specific "Our Global Footprint" and "Philosophy"
                content = content.replace('<h3>Our Global Footprint</h3>', '<h2>Our Global Footprint</h2>') # Likely has inline style
                # Regex for "Our Global Footprint"
                content = re.sub(r'<h3(.*?)>Our Global Footprint</h3>', r'<h2\1>Our Global Footprint</h2>', content)
                 # Regex for "Our Philosophy"
                content = re.sub(r'<h3(.*?)>Our Philosophy</h3>', r'<h2\1>Our Philosophy</h2>', content)

            # 7. Contact / Values: Promote "value-title" H3 -> H2
            # Occurs in contact.html ("Find Us", "Send Message") and others
            content = re.sub(r'<h3 class="value-title"(.*?)>(.*?)</h3>', r'<h2 class="value-title"\1>\2</h2>', content)

            # 8. Index / Schedule: Promote "day-title" H4 -> H3
            # Occurs in index.html for "Wednesday"/"Thursday"
            content = re.sub(r'<h4 class="day-title"(.*?)>(.*?)</h4>', r'<h3 class="day-title"\1>\2</h3>', content)

            # 9. Events.html: Promote "Register Now" and Card Titles H4 -> H3
            # Register Now has specific style or content
            content = content.replace('<h4>Register Now</h4>', '<h3>Register Now</h3>')
            content = re.sub(r'<h4(.*?)>Register Now</h4>', r'<h3\1>Register Now</h3>', content)
            
            # Sub-events in "More Events" are H4 (Milano Congress...)
            if file == "events.html":
                 # Card titles seem to be generic H4 with inline styles.
                 # Let's promote all H4 in events.html to H3, as there are no other H4s likely?
                 # Safest to target by content or structure if possible.
                 # Pattern: <h4 style="...">Milano...</h4>
                 content = re.sub(r'<h4(.*?)>(.*?)</h4>', r'<h3\1>\2</h3>', content)

            # 10. Guide Pages: "The Rhythm" (Highlight Box) H3 -> H2
            if "guide" in file:
                 content = content.replace('<h3>The Rhythm</h3>', '<h2>The Rhythm</h2>')
                 content = re.sub(r'<h3(.*?)>The Rhythm</h3>', r'<h2\1>The Rhythm</h2>', content)
                 # "Bachata Music" ?
                 content = re.sub(r'<h3(.*?)>Bachata Music</h3>', r'<h2\1>Bachata Music</h2>', content)
                 # "Key Elements" (Guide Sensual)
                 content = re.sub(r'<h3(.*?)>Key Elements</h3>', r'<h2\1>Key Elements</h2>', content)
                 
            # 11. Registration.html: Promote "timetable-day-header" H4 -> H3
            content = re.sub(r'<h4 class="timetable-day-header"(.*?)>(.*?)</h4>', r'<h3 class="timetable-day-header"\1>\2</h3>', content)

            # Retry Events H4 with DOTALL
            if file == "events.html":
                 # Target any H4 in events.html
                 content = re.sub(r'<h4(.*?)>(.*?)</h4>', r'<h3\1>\2</h3>', content, flags=re.DOTALL)

            # 12. Admin.html: Promote all H3 -> H2
            if file == "admin.html":
                 content = re.sub(r'<h3(.*?)>(.*?)</h3>', r'<h2\1>\2</h2>', content)

            # 13. Room Rental / Corporate: Promote "section-title-modern" H3 -> H2
            # Use DOTALL for multi-line support
            if file == "room-rental.html" or file == "corporate-events.html":
                 content = re.sub(r'<h3 class="section-title-modern"(.*?)>(.*?)</h3>', r'<h2 class="section-title-modern"\1>\2</h2>', content, flags=re.DOTALL)

            # 14. Blog Posts: Promote H3 -> H2
            if "blog-posts" in root or file.startswith("blog-"):
                 content = re.sub(r'<h3(.*?)>(.*?)</h3>', r'<h2\1>\2</h2>', content)
                 
            # 15. About.html: Fix H4 in JS string & H3 -> H2
            if file == "about.html":
                content = content.replace("'<h4 ", "'<h3 ")
                content = content.replace("</h4><ul", "</h3><ul")
                # Promote any remaining H3 to H2
                content = re.sub(r'<h3(.*?)>(.*?)</h3>', r'<h2\1>\2</h2>', content)

            # 16. Room Rental: Promote H4 -> H3 (Since we promoted parent H3->H2)
            if file == "room-rental.html":
                content = re.sub(r'<h4(.*?)>(.*?)</h4>', r'<h3\1>\2</h3>', content)

            # 17. Corporate Events: Promote H3 -> H2 (Retry generic H3)
            if file == "corporate-events.html":
                content = re.sub(r'<h3(.*?)>(.*?)</h3>', r'<h2\1>\2</h2>', content)






                
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed headings in: {file}")
                count += 1
                
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    fix_headings()
