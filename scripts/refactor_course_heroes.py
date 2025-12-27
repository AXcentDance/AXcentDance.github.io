import os
import re

# Pages to refactor (Standard .course-hero pattern)
TARGET_FILES = [
    "bachata-beginner-0.html",
    "bachata-beginner-2.html",
    "bachata-sensual-foundation.html",
    "bachata-sensual-improver.html",
    "bachata-sensual-inter-adv.html",
    "guide-bachata-sensual.html",
    "guide-bachata.html",
    "lady-styling.html"
]

ROOT_DIR = "/Users/slamitza/AXcentWebsiteGitHub"

def refactor_file(filename):
    filepath = os.path.join(ROOT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename} (Not found)")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find <section class="course-hero"> ... <div class="container course-hero-content">
    # We want to replace opening of section and inject image
    
    # Pattern:
    # <section class="course-hero">\s*<div class="container course-hero-content">
    
    # Replacement:
    # <section class="course-hero relative-container" style="background: none;">
    #   <img src="assets/images/schedule_hero_placeholder.webp" alt="Bachata Class Zurich" class="hero-bg-img" loading="eager">
    #   <div class="hero-overlay"></div>
    #   <div class="container course-hero-content hero-content-z">
    
    pattern = r'(<section class="course-hero"(?: style="[^"]*")?>)\s*<div class="container course-hero-content">'
    
    match = re.search(pattern, content)
    if match:
        original_section_tag = match.group(1)
        
        # Check if already refactored
        if "relative-container" in original_section_tag:
            print(f"Skipping {filename} (Already refactored)")
            return

        # Prepare new section tag
        # Add relative-container
        if "style=" in original_section_tag:
            new_section_tag = original_section_tag.replace('class="course-hero"', 'class="course-hero relative-container"').replace('style="', 'style="background: none; ')
        else:
            new_section_tag = original_section_tag.replace('class="course-hero"', 'class="course-hero relative-container" style="background: none;"')
            
        replacement = f"""{new_section_tag}
      <img src="assets/images/schedule_hero_placeholder.webp" alt="Bachata Dance Class Zurich" class="hero-bg-img" loading="eager">
      <div class="hero-overlay"></div>
      <div class="container course-hero-content hero-content-z">"""
      
        new_content = re.sub(pattern, replacement, content, count=1)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Refactored {filename}")
        
    else:
        print(f"Pattern not found in {filename}")

if __name__ == "__main__":
    for file in TARGET_FILES:
        refactor_file(file)
