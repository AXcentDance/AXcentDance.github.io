
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

ALT_TRANSLATIONS = {
    # Events
    "Milano Sensual Congress 2026 Flyer": "Milano Sensual Congress 2026 Flyer", # Keep mostly same or add details
    "Milano Sensual Congress Spring Edition Flyer": "Milano Sensual Congress Spring Edition Flyer",
    "Bootcamp": "Bootcamp", # German understands Bootcamp
    "MSC Nov 2026": "MSC Nov 2026",
    
    # Generic / Social
    "Social dancing moment at AXcent Dance": "Social Dancing Moment bei AXcent Dance",
    "Social Dancing in Zürich": "Social Dancing in Zürich",
    "Group selfie at dance event": "Gruppen-Selfie bei einem Tanzevent",
    "Large group photo after class": "Gruppenfoto nach dem Tanzkurs",
    "Stage performance at festival": "Bühnenauftritt beim Festival",
    "Students and instructors posing at an international dance festival": "Schüler und Lehrer posieren bei einem internationalen Tanzfestival",
    "Students learning new partnerwork moves in class": "Schüler lernen neue Partnerwork-Figuren im Kurs",
    "Students practicing footwork in the dance studio mirror": "Schüler üben Footwork im Spiegel des Tanzstudios",
    "The AXcent Dance team lineup ready for performance": "Das AXcent Dance Team bereit für den Auftritt",
    "Happy couple dancing Bachata at sunset": "Glückliches Paar tanzt Bachata bei Sonnenuntergang",
    "Social dancing night at AXcent Dance Zurich with happy dancers": "Social Dancing Abend bei AXcent Dance Zürich mit glücklichen Tänzern",
    
    # Wedding / Private
    "Wedding Dance Couple": "Hochzeitstanz Paar",
    "Private Dance Lessons Zurich": "Privatstunden Zürich",
    "Private Lesson Coach": "Privatstunden Lehrer",
    
    # Blog / Misc
    "New Location Zurich": "Neuer Standort Zürich",
    "Christmas Break": "Weihnachtspause",
    "Frame Technique": "Rahmen-Technik",
    "Connection 101": "Verbindung 101",
    "Bachata Roots": "Bachata Wurzeln",
    "First Week at AXcent Dance New Studio": "Erste Woche im neuen AXcent Dance Studio",
    "Stress Less, Dance More": "Weniger Stress, Mehr Tanzen",
    "Romeo Santos Tour 2026": "Romeo Santos Tour 2026", # Names usually stay
    "Dance Essentials Flatlay": "Tanz-Essentials Flatlay",
    "Requinto Gitarre": "Requinto Gitarre", # Already de?
    "Segunda Gitarre": "Segunda Gitarre",
    
    # Hero/Stock
    "Bachata Dancers": "Bachata Tänzer",
    "Latin Dance Class": "Latin Tanzkurs",
    "Dance Studio Zurich": "Tanzstudio Zürich"
}

def localize_alt_text():
    print("Localizing Image Alt Text in /de/...")
    
    files_changed = 0
    
    # Walk all files in /de/
    de_files = []
    for root, dirs, files in os.walk(DE_DIR):
        for file in files:
            if file.endswith('.html'):
                de_files.append(os.path.join(root, file))
                
    for filepath in de_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Replace Alt Text
        # alt="Text" -> alt="Translated"
        
        for en, de in ALT_TRANSLATIONS.items():
            # Robust replacement for exact string match inside quotes
            # We can use simple replace if string is unique enough,
            # but safer to ensure it's an alt attribute context?
            # Actually, standard string replace is low risk for these phrases.
            
            if en in content:
                # Check if it's already translated (if en == de, no chg)
                if en != de:
                    # Replace only inside alt="..." ideally, but global replace is acceptable here for these specific strings
                   content = content.replace(f'alt="{en}"', f'alt="{de}"')
                   
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{os.path.basename(filepath)}] Localized Alt Text.")
            files_changed += 1

    print(f"Finished. Updated {files_changed} files.")

if __name__ == "__main__":
    localize_alt_text()
