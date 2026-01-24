
import os
import json
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'

def check_german_schema(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find JSON-LD scripts
    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
    
    for script in scripts:
        try:
            data = json.loads(script)
            # Check description field
            desc = data.get('description', '')
            if desc and "Bachata" in desc: # Basic check
                # Heuristic: Detect English words "Learn", "The", "and" vs "Lernen", "Der", "und"
                # Very rough.
                
                english_indicators = ['Learn', 'The', ' and ', ' with ', ' about ']
                german_indicators = ['Lernen', 'Der', ' und ', ' mit ', ' über ', 'Zürich']
                
                en_score = sum(1 for w in english_indicators if w in desc)
                de_score = sum(1 for w in german_indicators if w in desc)
                
                if en_score > de_score:
                    print(f"[POTENTIAL EN SCHEMA] {os.path.basename(filepath)}: {desc[:60]}...")
                    
        except:
            pass

def main():
    print("Checking German pages for English Schema...")
    de_dir = os.path.join(ROOT_DIR, 'de')
    for root, dirs, files in os.walk(de_dir):
        for file in files:
            if file.endswith('.html'):
                check_german_schema(os.path.join(root, file))

if __name__ == "__main__":
    main()
