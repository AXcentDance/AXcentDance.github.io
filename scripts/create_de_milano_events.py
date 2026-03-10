import os
import re

def create_de_event_page(src_path, dest_path, substitutions):
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply translations
    for en, de in substitutions.items():
        content = content.replace(en, de)

    # Specific fixes for relative paths in /de/
    content = content.replace('href="style.css', 'href="../style.css')
    content = content.replace('src="script.js', 'src="../script.js')
    content = content.replace('href="about"', 'href="about"') # These will be fixed by fix_german_links
    content = content.replace('href="/"', 'href="/de/"')
    
    # Fix lang attribute
    content = content.replace('<html lang="en">', '<html lang="de">')

    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created German event page: {dest_path}")

def main():
    root = '/Users/slamitza/AXcentWebsiteGitHub'
    
    # 1. Milano 2026
    subs1 = {
        'Upcoming Events': 'Bevorstehende Events',
        'Join the AXcent Dance family at international congresses. We organize group trips, shared accommodation, and exclusive discounts for our students.': 'Tritt der AXcent Dance Familie bei internationalen Kongressen bei. Wir organisieren Gruppenreisen, gemeinsame Unterkünfte und exklusive Rabatte für unsere Schüler.',
        'Group Trip • Nov 20-21-22, 2026 • <span style="color: var(--accent-start);">Join Us</span>': 'Gruppenreise • 20.-22. Nov 2026 • <span style="color: var(--accent-start);">Sei dabei</span>',
        'Experience the magic of <strong>Milano Sensual Congress</strong> with us!': 'Erlebe die Magie des <strong>Milano Sensual Congress</strong> mit uns!',
        "It's one of the most prestigious Bachata Sensual events in the world": 'Es ist eines der prestigeträchtigsten Bachata Sensual Events der Welt',
        'featuring top world artists': 'mit internationalen Top-Künstlern',
        "Don't miss the <strong>3 hours of Masterclass</strong>": 'Verpasse nicht die <strong>3 Stunden Masterclass</strong>',
        'with participants from all over Europe!': 'mit Teilnehmern aus ganz Europa!',
        'Location': 'Ort',
        'Type': 'Typ',
        'Date': 'Datum',
        'Discount Code': 'Rabatt-Code',
        'BUY NOW': 'JETZT KAUFEN',
        'More Events': 'Weitere Events',
        'Events': 'Events',
        'About us': 'Über uns',
        'Schedule': 'Stundenplan',
        'Registration': 'Anmeldung',
        'Contact': 'Kontakt',
        'More ▾': 'Mehr ▾',
        'Room Rental': 'Raumvermietung',
        'Corporate Events': 'Firmenevents',
        'Wedding Dance': 'Hochzeitstanz',
        'Private Lessons': 'Privatstunden',
        'Gallery': 'Galerie',
        'Education': 'Ausbildung',
        'Beginner Guide': 'Anfänger Guide',
        'Blog': 'Blog',
        'FAQ': 'FAQ',
        'Dance Etiquette': 'Tanzetikette',
        'Book Free Trial': 'Kostenlose Probelektion',
        'What is Bachata': 'Was ist Bachata',
        'Roots of Bachata': 'Wurzeln des Bachata',
        'Class Schedule': 'Stundenplan',
        'Our Blog': 'Unser Blog',
        'Terms & Conditions': 'AGB',
        'Privacy Policy': 'Datenschutz',
        'Imprint': 'Impressum',
        'Full Pass + Hotel': 'Full Pass + Hotel',
        'Milan, Italy': 'Mailand, Italien'
    }
    
    create_de_event_page(
        os.path.join(root, 'Milano-Sensual-Congress-2026.html'),
        os.path.join(root, 'de', 'Milano-Sensual-Congress-2026.html'),
        subs1
    )

    # 2. Milano Spring 2026
    subs2 = {
        'Upcoming Events': 'Bevorstehende Events',
        'Join the AXcent Dance family for a special Spring Edition of the Milano Sensual Congress.': 'Tritt der AXcent Dance Familie bei für eine spezielle Spring Edition des Milano Sensual Congress.',
        'Group Trip • May 15-17, 2026 • <span style="color: var(--accent-start);">Join Us</span>': 'Gruppenreise • 15.-17. Mai 2026 • <span style="color: var(--accent-start);">Sei dabei</span>',
        'Get ready for the <strong>Spring Edition</strong> of the Milano Sensual Congress!': 'Mach dich bereit für die <strong>Spring Edition</strong> des Milano Sensual Congress!',
        'We are bringing you another unforgettable experience': 'Wir bescheren dir ein weiteres unvergessliches Erlebnis',
        'with some of the best artists in the world': 'mit einigen der besten Künstler der Welt',
        'Location': 'Ort',
        'Type': 'Typ',
        'Date': 'Datum',
        'Discount Code': 'Rabatt-Code',
        'BUY NOW': 'JETZT KAUFEN',
        'More Events': 'Weitere Events',
        'Milan, Italy': 'Mailand, Italien'
    }
    # Add common navigation translations to subs2
    subs2.update({k: v for k, v in subs1.items() if k not in subs2})

    create_de_event_page(
        os.path.join(root, 'Milano-Sensual-Congress-Spring-2026.html'),
        os.path.join(root, 'de', 'Milano-Sensual-Congress-Spring-2026.html'),
        subs2
    )

if __name__ == "__main__":
    main()
