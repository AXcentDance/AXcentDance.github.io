
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_FAQ_PATH = os.path.join(ROOT_DIR, 'de', 'faq.html')

FAQ_TRANSLATIONS = {
    # Questions
    "Do I need a partner to join?": "Brauche ich einen Partner, um teilzunehmen?",
    "What should I wear?": "Was soll ich anziehen?",
    "I have never danced before. Can I join?": "Ich habe noch nie getanzt. Kann ich mitmachen?",
    "How do I pay for classes?": "Wie bezahle ich für die Kurse?",
    "Is there parking available?": "Gibt es Parkplätze?",
    "What if I miss a class?": "Was passiert, wenn ich eine Stunde verpasse?",
    
    # Answers (Keywords)
    "No, you do not need a partner.": "Nein, du brauchst keinen Partner.",
    "Comfortable clothing": "Bequeme Kleidung",
    "Absolutely!": "Absolut!",
    "We accept cash, TWINT, and credit cards.": "Wir akzeptieren Barzahlung, TWINT und Kreditkarten."
}

def translate_faq_schema():
    print("Translating FAQ Schema...")
    
    if not os.path.exists(DE_FAQ_PATH):
        print("FAQ file not found.")
        return

    with open(DE_FAQ_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original_content = content
    
    # Replace Questions in Schema
    # "name": "Do I need a partner to join?"
    for en, de in FAQ_TRANSLATIONS.items():
        # strict replacement
        content = content.replace(f'"{en}"', f'"{de}"')
        
    if content != original_content:
        with open(DE_FAQ_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated FAQ Schema translations.")
    else:
        print("No changes needed in FAQ Schema.")

if __name__ == "__main__":
    translate_faq_schema()
