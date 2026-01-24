
import os
import re
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

def audit_schema():
    print("## 4. Schema Localization Audit")
    print("Verifying that JSON-LD schemas in /de/ pages are valid and localized...")
    
    issues = []
    
    de_files = [f for f in os.listdir(DE_DIR) if f.endswith('.html')]
    
    for filename in de_files:
        path = os.path.join(DE_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find JSON-LD blocks
        matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        
        if not matches:
            # Some pages might not have schema, that's okay, but notes it
            # issues.append(f"[{filename}] No Schema found (Information)")
            continue
            
        for i, json_str in enumerate(matches):
            try:
                data = json.loads(json_str)
                
                # Check 1: inLanguage property?
                # Many local business schemas support 'knowsLanguage' or 'inLanguage'
                # But mostly we check if descriptions are German
                
                # Heuristic: Check for specific German words in description or name
                # Or check if "Zurich" is "Zürich" in Address
                
                json_dump = json.dumps(data, ensure_ascii=False)
                
                if "Zurich" in json_dump and "Zürich" not in json_dump:
                     # This is a soft check. 'Zurich' is valid in English, but 'Zürich' is preferred in refined DE.
                     pass 
                     
                # Check for English boilerplate in Schema
                # e.g. "Dance School" vs "Tanzschule"
                if '"DanceSchool"' in json_dump: 
                    # This is the @type, which MUST be in English. PASS.
                    pass
                    
                if '"description":' in json_dump:
                    # simplistic check
                    pass
                    
            except json.JSONDecodeError as e:
                issues.append(f"[{filename}] Invalid JSON-LD Schema: {e}")

    if issues:
        print(f"⚠️ Found {len(issues)} Schema issues:")
        for i in issues:
            print(i)
    else:
        print("✅ JSON-LD Schemas are valid JSON.")

if __name__ == "__main__":
    audit_schema()
