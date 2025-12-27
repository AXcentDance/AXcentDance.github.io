import sys
import os
import datetime

# Import sibling scripts by adding current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import seo_audit
import broken_link_checker
import image_seo_checker
import heading_structure_checker
import advanced_image_checker

# Define output path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, "System", "SEO_Audit_Report.md")

def main():
    # Capture standard output
    original_stdout = sys.stdout
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            sys.stdout = f
            
            print(f"# AXcent Dance Website - Clean SEO Report")
            print(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"**Location:** `System/SEO_Audit_Report.md`\n")
            
            print("## 1. SEO Metadata Audit")
            print("Checking Titles and Meta Descriptions...")
            print("```text")
            # seo_audit takes root_dir as argument
            seo_audit.audit_seo(ROOT_DIR)
            print("```\n")
            
            print("## 2. Broken Internal Links")
            print("Validating all internal hrefs and checking for dead links...")
            print("```text")
            # Other scripts use their own internal ROOT_DIR constant, which should match
            broken_link_checker.check_broken_links()
            print("```\n")
            
            print("## 3. Image Optimization")
            print("Checking Alt tags and non-WebP formats...")
            print("```text")
            image_seo_checker.check_image_seo()
            print("```\n")
            
            print("## 4. Heading Structure")
            print("Validating H1-H6 hierarchy order...")
            print("```text")
            heading_structure_checker.check_headings()
            print("```\n")
            
            print("## 5. Advanced Image Quality Audit")
            print("Checking for Image Count, Alt Text, and Responsive Attributes...")
            print("```text")
            advanced_image_checker.check_advanced_image_quality()
            print("```\n")
            
    except Exception as e:
        sys.stdout = original_stdout # Restore before printing error
        print(f"Error generating report: {e}")
        return

    sys.stdout = original_stdout
    print(f"Report successfully generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
