
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DE_DIR = os.path.join(ROOT_DIR, 'de')

# List of strings that DEFINITELY should be German in the /de/ directory.
# If these English words appear, it suggests a missed translation.
# Excluding common false positives.
GHOST_STRINGS = [
    "Read More",
    "Book Now",
    "Contact Us",
    "Privacy Policy",
    "Terms & Conditions",
    "Follow us",
    "All rights reserved",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
    "About Us",
    "Schedule",
    "Classes",
    "Home",
    "See more",
    "Register", 
    "Full Pass",
    "Party Pass",
    "Workshops",
]

# Allow-list for valid uses (e.g. names of songs, unexpected contexts)
EXCLUSIONS = [
    "Milano Sensual Congress" # Event name
]

def audit_ghost_content():
    print("## 3. Ghost Content (Untranslated Strings) Audit")
    print("Scanning for common English UI strings left in German pages...")
    
    issues = []
    
    de_files = [f for f in os.listdir(DE_DIR) if f.endswith('.html')]
    
    for filename in de_files:
        path = os.path.join(DE_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove scripts and styles to avoid parsing code variables
        # Simple/naive strip
        content_stripped = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
        content_stripped = re.sub(r'<style.*?>.*?</style>', '', content_stripped, flags=re.DOTALL)
        
        for ghost in GHOST_STRINGS:
            # Case insensitive search but word boundary? 
            # Often they are inside tags >Read More<
            # Let's search for >GhostString< or just GhostString
            
            if ghost in content_stripped:
                # Check for context (is it in an English quote?)
                # For now just flag it
                issues.append(f"[{filename}] Found potential untranslated string: '{ghost}'")

    if issues:
        print(f"⚠️ Found {len(issues)} potential translation misses:")
        for i in issues:
            print(i)
        print("\n(Note: Some might be false positives if they are proper names or song titles)")
    else:
        print("✅ No common English ghost strings found.")

if __name__ == "__main__":
    audit_ghost_content()
