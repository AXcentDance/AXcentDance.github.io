
import os
import json
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

# Translations map (Filename -> { 'EN start': 'DE translation' })
# We match loosely by substring or use specific full text replacement
TRANSLATIONS = {
    'de/events.html': {
        "Upcoming Bachata events, workshops, and congresses": "Kommende Bachata-Events, Workshops und Kongresse, organisiert von und mit AXcent Dance Zürich. Verpasse keine Party!"
    },
    'de/blog-posts/romeo-prince-tour-2026.html': {
        "The Kings of Bachata are back! Official dates": "Die Könige des Bachata sind zurück! Offizielle Daten für die 'Mejor Tarde Que Nunca' Tour von Romeo Santos & Prince Royce."
    },
    'de/blog-posts/what-to-wear-bachata.html': {
        "Wondering what to wear for your first Bachata class?": "Fragst du dich, was du zu deiner ersten Bachata-Stunde anziehen sollst? Hier ist unser kompletter Guide zu Kleidung, Schuhen und Hygiene."
    },
    'de/blog-posts/science-of-dance-mental-health.html': {
        "Discover the science behind how partner dancing like Bachata": "Entdecke die Wissenschaft dahinter, wie Paartanz wie Bachata Cortisol senkt, Endorphine freisetzt und die mentale Gesundheit verbessert."
    },
    'de/blog-posts/roots-of-bachata.html': {
        "Discover where Bachata was born, why it was prohibited": "Entdecke, wo Bachata geboren wurde, warum er in der Vergangenheit verboten war, und seine Geschichte von den dominikanischen Wurzeln zum globalen Tanzphänomen."
    },
    'de/blog-posts/dance-tips-1-frame.html': {
        "Improve your Bachata leading and following with better frame": "Verbessere dein Bachata Führen und Folgen mit besserer Rahmen-Technik. Lerne die Do's und Don'ts für Positionierung und Verbindung."
    }
}

def localize_schema(rel_path):
    filepath = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(filepath): return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find translations for this file
    file_map = TRANSLATIONS.get(rel_path.replace('\\', '/'), {})
    if not file_map: return

    # Simple string replacement for safety in JSON
    # We must match the English text in the file
    
    new_content = content
    for en_text, de_text in file_map.items():
        # Look for the EN text in existing content
        # It's inside a JSON string, so characters shouldn't be too escaped hopefully
        # But we only matched a prefix in the definition above.
        
        # Regex to find the full description value starting with the known EN text
        # "description": "Known EN text......."
        
        # Escape EN text for regex
        en_escaped = re.escape(en_text)
        
        # Capture full content of description until end quote
        # pattern: "description"\s*:\s*"({en_escaped}[^"]*)"
        pattern = re.compile(r'("description"\s*:\s*")(' + en_escaped + r'[^"]*)(")')
        
        match = pattern.search(new_content)
        if match:
            # Replace with DE text
            # We preserve the key and quotes, just replace group 2
            # CAUTION: The DE text should be just the translation.
            # Use the provided DE text directly.
            
            replacement = f'\\1{de_text}\\3'
            new_content = pattern.sub(replacement, new_content)
            print(f"Localized '{en_text[:20]}...' in {rel_path}")
        else:
            print(f"Could not find match for '{en_text[:20]}...' in {rel_path}")

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def main():
    print("Localizing Schema...")
    for rel_path in TRANSLATIONS.keys():
        localize_schema(rel_path)

if __name__ == "__main__":
    main()
