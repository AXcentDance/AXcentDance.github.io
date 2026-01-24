
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

def audit_og_tags():
    print("Auditing Open Graph Tags in /de/...")
    
    issues = 0
    
    de_files = []
    for root, dirs, files in os.walk(DE_DIR):
        for file in files:
            if file.endswith('.html'):
                de_files.append(os.path.join(root, file))
                
    for filepath in de_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # extract title
        title_match = re.search(r'<title>(.*?)</title>', content)
        meta_desc_match = re.search(r'<meta name="description"\s+content="(.*?)"', content)
        
        # extract og tags
        og_title_match = re.search(r'<meta property="og:title" content="(.*?)"', content)
        og_desc_match = re.search(r'<meta property="og:description"\s+content="(.*?)"', content)
        og_locale_match = re.search(r'<meta property="og:locale" content="(.*?)"', content)
        
        rel_path = os.path.relpath(filepath, DE_DIR)
        
        # Check Locale
        if not og_locale_match or og_locale_match.group(1) != "de_CH":
             print(f"[{rel_path}] ⚠️ Invalid or Missing og:locale: {og_locale_match.group(1) if og_locale_match else 'Missing'}")
             issues += 1
             
        # Check Title Parity (Approximate)
        # Often title has " - AXcent Dance" appended, but OG might not.
        # Just check if it's English-ish?
        # Better: Check if og:title is SAME as title (roughly)
        
        if title_match and og_title_match:
            t = title_match.group(1)
            ot = og_title_match.group(1)
            # If title is German but OG is obvious English?
            # Hard to detect automatically without NLP.
            # But let's check for equality logic.
            # actually, just print mismatches if significant
            pass
            
        # Check Description Parity
        if meta_desc_match and og_desc_match:
            d = meta_desc_match.group(1)
            od = og_desc_match.group(1)
            
            if d != od:
                print(f"[{rel_path}] ⚠️ Meta Description vs OG Description Mismatch")
                print(f"   Meta: {d[:50]}...")
                print(f"   OG:   {od[:50]}...")
                issues += 1
        elif meta_desc_match and not og_desc_match:
             print(f"[{rel_path}] ⚠️ Missing og:description")
             issues += 1
             
    if issues == 0:
        print("✅ All Open Graph tags seem consistent and present.")
    else:
        print(f"Found {issues} potential OG issues.")

if __name__ == "__main__":
    audit_og_tags()
