
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

TRANSLATIONS = {
    # Nav & Footer
    ">Home<": ">Startseite<", # Context aware (in nav)
    ">Privacy Policy<": ">Datenschutz<",
    ">Terms & Conditions<": ">AGB<",
    ">Terms<": ">AGB<",
    ">All rights reserved<": ">Alle Rechte vorbehalten<",
    ">Follow us<": ">Folge uns<", 
    
    # Days / Months
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag", 
    "Saturday": "Samstag",
    "Sunday": "Sonntag",
    "January": "Januar", "February": "Februar", "March": "März", "April": "April", 
    "May": "Mai", "June": "Juni", "July": "Juli", "August": "August", 
    "September": "September", "October": "Oktober", "November": "November", "December": "Dezember",

    # Common UI
    ">Schedule<": ">Stundenplan<",
    ">Classes<": ">Kurse<",
    ">Workshops<": ">Workshops<", # Same but included for completeness check
    ">Read More<": ">Mehr lesen<",
    ">Book Now<": ">Jetzt buchen<",
    ">See more<": ">Mehr ansehen<"
}

def translate_ghosts():
    print("Translating Ghost Content...")
    
    de_files = [f for f in os.listdir(DE_DIR) if f.endswith('.html')]
    
    files_changed = 0
    
    for filename in de_files:
        filepath = os.path.join(DE_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for en_term, de_term in TRANSLATIONS.items():
            # Special handling for >String< keys to ensure we only replace text content
            if en_term.startswith(">") and en_term.endswith("<"):
                 content = content.replace(en_term, de_term)
            else:
                 # Be careful with simple words like "May" (could be logic).
                 # Only replace if surrounded by non-word chars or specific tags?
                 # Safest is simply string replacement if we are confident it's content.
                 # Given the audit found them in specific places, let's try strict regex for words
                 
                 pattern = r'(?<![a-zA-Z])' + re.escape(en_term) + r'(?![a-zA-Z])'
                 # But don't replace inside HTML attributes! This is hard with regex.
                 
                 # Simpler approach: Verify exact context where they usually appear
                 # e.g. <div class="date">May</div>
                 
                 # For now, let's rely on string replacement but audit strictly?
                 # No, too risky for "May".
                 
                 # Let's restrict non-tagged replacements to known safe ones
                 if en_term in ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                     content = content.replace(en_term, de_term)
                 elif en_term in ["January", "February", "March", "October", "December"]: # Safe ish
                     content = content.replace(en_term, de_term)
                 elif en_term == "May":
                     # Replace ">May<" or " May "
                     content = content.replace(">May<", ">Mai<")
                     content = content.replace(" May ", " Mai ")
                 elif en_term == "June":
                     content = content.replace("June", "Juni")
                 elif en_term == "July":
                     content = content.replace("July", "Juli")
                     
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{filename}] Updated translations.")
            files_changed += 1
            
    print(f"Finished. Updated {files_changed} files.")

if __name__ == "__main__":
    translate_ghosts()
