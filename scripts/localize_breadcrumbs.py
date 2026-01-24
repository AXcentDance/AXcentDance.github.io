
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

# Mapping for Breadcrumb Names (JSON-LD and Visual)
BREADCRUMB_MAP = {
    # Base
    "Home": "Startseite",
    "AXcent Dance": "Startseite", # Sometimes used as Home in schema
    
    # Categories
    "Services": "Angebot",
    "Classes": "Kurse",
    "Events": "Events",
    "Resources": "Ressourcen",
    "Blog": "Blog",
    "Legal": "Rechtliches",
    "About": "Über uns",
    "Contact": "Kontakt",
    
    # Specific Pages
    "Private Lessons": "Privatstunden",
    "Wedding Dance": "Hochzeitstanz",
    "Gallery": "Galerie",
    "FAQ": "FAQ",
    "Etiquette": "Etikette",
    "Room Rental": "Raumvermietung",
    "Corporate Events": "Firmenevents",
    "Beginner Guide": "Anfänger Guide",
    "Bachata Guide": "Bachata Guide",
    "Bachata Sensual Guide": "Bachata Sensual Guide",
    "Education": "Ausbildung",
    "Registration": "Anmeldung",
    "Terms": "AGB",
    "Privacy": "Datenschutz",
    "Imprint": "Impressum",
    
    # Course Levels
    "Beginner 0": "Anfänger 0",
    "Beginner 2": "Anfänger 2",
    "Foundations": "Grundlagen",
    "Improver": "Improver", 
    "Intermediate/Advanced": "Mittelstufe/Fortgeschritten",
    "Lady Styling": "Lady Styling"
}

def localize_breadcrumbs():
    print("Starting Breadcrumb Localization...")
    
    de_files = [f for f in os.listdir(DE_DIR) if f.endswith('.html')]
    
    files_changed = 0
    
    for filename in de_files:
        filepath = os.path.join(DE_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # 1. LOCALIZING JSON-LD SCHEMA
        # Look for "name": "EnglishName" inside BreadcrumbList
        # This is tricky with simple regex, but we can target specific patterns or use strict replacement
        # given we know the schema structure is consistent.
        
        # Pattern: "name": "VALUE"
        # We iterate over our map
        for en_name, de_name in BREADCRUMB_MAP.items():
            # Replace "name": "Home" -> "name": "Startseite"
            # We strictly target quoted JSON property
            
            # Be careful not to replace in other contexts? 
            # Ideally we only do this inside the <script type="application/ld+json"> block.
            
            def schema_replacer(match):
                block = match.group(0)
                # Apply replacements only inside the block
                for en, de in BREADCRUMB_MAP.items():
                    # Replace "name": "English" with "name": "German"
                    # But also "item": "https://axcentdance.com/" -> "item": "https://axcentdance.com/de/" for Home?
                    
                    # NAME REPLACEMENT
                    block = block.replace(f'"name": "{en}"', f'"name": "{de}"')
                    
                # URL REPLACEMENT FOR ALL ITEMS
                # "item": "https://axcentdance.com/some-page" -> "item": "https://axcentdance.com/de/some-page"
                
                # We need to be careful. Some pages might already be localized or relative.
                # But typically schema has absolute URLs.
                
                # Strategy: If the URL does NOT contain /de/, insert it.
                # But only for internal links.
                
                def url_fixer(url_match):
                    url = url_match.group(1)
                    if "axcentdance.com" in url and "/de/" not in url:
                        # Insert /de/ after .com/
                        return f'"item": "{url.replace("axcentdance.com/", "axcentdance.com/de/")}"'
                    return url_match.group(0)

                # Replace "item": "URL"
                block = re.sub(r'"item": "(https://axcentdance\.com/[^"]+)"', url_fixer, block)
                
                return block

            content = re.sub(r'<script type="application/ld\+json">(.*?)</script>', schema_replacer, content, flags=re.DOTALL)


        # 2. VISUAL BREADCRUMBS
        # Often contain <a href="/">Home</a>
        # We need to find the visual breadcrumb section.
        # It's usually marked by class "breadcrumb" or similar, or just links.
        # The user's grep showed <!-- Visual Breadcrumbs --> comment.
        
        if "<!-- Visual Breadcrumbs -->" in content:
            # We assume a block following this comment
            # Let's target links like <a href="/">Home</a>
            
            def visual_replacer(match):
                # match is the whole breadcrumb block roughly? 
                # No, let's just do global replacement for specifically breadcrumb-like links
                # if we can identify them.
                pass
            
            # Simple global Replacements for DE context
            # <a href="/">Home</a> -> <a href="/de/">Startseite</a>
            # <a href="index.html">Home</a> -> <a href="index.html">Startseite</a>
            
            content = content.replace('<a href="/">Home</a>', '<a href="/de/">Startseite</a>')
            content = content.replace('<a href="/de/">Home</a>', '<a href="/de/">Startseite</a>')
            content = content.replace('<a href="../">Home</a>', '<a href="../de/">Startseite</a>') # If relative? index is in DE
            
            # Also replace intermediate crumbs if they exist
            # e.g. <a href="events">Events</a> -> <a href="events">Events</a> (Same word)
            # <a href="classes">Classes</a> -> <a href="classes">Kurse</a>
            
            content = content.replace('>Classes</a>', '>Kurse</a>')
            content = content.replace('>Resources</a>', '>Ressourcen</a>')
            content = content.replace('>Legal</a>', '>Rechtliches</a>')
            
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{filename}] Localized breadcrumbs.")
            files_changed += 1
        else:
            print(f"[{filename}] No breadcrumb changes.")

    print(f"Finished. Updated {files_changed} files.")

if __name__ == "__main__":
    localize_breadcrumbs()
