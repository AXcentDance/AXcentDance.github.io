import os
import glob
import re

STYLE_BLOCK = """  <!-- CRITICAL: FAIL-SAFE MOBILE MENU STYLES -->
  <style>
    /* DESKTOP (900px+) - HIDE BUTTON */
    @media (min-width: 900px) {
      .mobile-menu-btn {
        display: none !important;
      }
    }

    /* MOBILE (<900px) - SHOW BUTTON ABSOLUTE LEFT */
    @media (max-width: 899px) {
      .navbar {
        position: relative !important;
        /* Ensure anchor */
        justify-content: center !important;
        /* Center logo */
      }

      .mobile-menu-btn {
        display: flex !important;
        position: absolute !important;
        /* Absolute to navbar */
        top: 50% !important;
        transform: translateY(-50%) !important;
        left: 15px !important;
        z-index: 10001 !important;

        background: transparent !important;
        border: none !important;
        color: white !important;

        width: 44px;
        height: 44px;
        align-items: center;
        justify-content: center;
        padding: 0;
        cursor: pointer;
      }

      /* Ensure SVG is visible */
      .mobile-menu-btn svg {
        width: 30px !important;
        height: 30px !important;
        stroke: white !important;
        display: block !important;
      }
    }
  </style>"""

def sync_styles():
    files = glob.glob("*.html")
    count = 0
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove existing block if present to avoid dupes (regex matches the comment start and </style> end)
            content = re.sub(r'<!-- CRITICAL: FAIL-SAFE MOBILE MENU STYLES -->.*?<\/style>\s*', '', content, flags=re.DOTALL)
            
            # Inject new block before </head>
            if '</head>' in content:
                content = content.replace('</head>', STYLE_BLOCK + '\n</head>')
                
                # Update cache buster
                content = re.sub(r'style\.css\?v=mobilefix\d+', 'style.css?v=mobilefix12', content)
                
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {file}")
                count += 1
            else:
                print(f"Skipping {file} (no </head>)")
        except Exception as e:
            print(f"Error processing {file}: {e}")

    print(f"Successfully processed {count} files.")

if __name__ == "__main__":
    sync_styles()
