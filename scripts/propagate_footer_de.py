
import os
import re

ROOT_DIR = '/Users/slamitza/AXcentWebsiteGitHub'
DE_DIR = os.path.join(ROOT_DIR, 'de')

# The master footer template from de/registration.html
# Note: we use placeholders for links that need to be relative
FOOTER_TEMPLATE = """    <footer class="main-footer">
        <div class="container footer-grid">
            <div class="footer-col">
                <a href="{prefix}index.html" class="logo footer-logo"><span class="logo-title">AXCENT</span><span
                        class="logo-subtitle text-gradient">DANCE</span></a>
                <p class="footer-address">
                    Hermetschloostrasse 73,<br>
                    8048 Zurich Altstetten<br> 2 Minuten zu Fuss von Tram 2 und Bus 31 Haltestelle
                </p>
                <div class="footer-socials">
                    <a href="https://www.instagram.com/axcent_dance/" target="_blank" aria-label="Instagram">
                        <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                            <path
                                d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                        </svg>
                    </a>
                    <a href="mailto:info@axcentdance.com" aria-label="Email">
                        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z">
                            </path>
                        </svg>
                    </a>
                </div>
            </div>

            <div class="footer-col">
                <h2 class="footer-heading">Schnellzugriff</h2>
                <ul class="footer-links">
                    <li><a href="{prefix}guide-bachata.html">Was ist Bachata</a></li>
                    <li><a href="{prefix}blog-posts/roots-of-bachata.html">Wurzeln des Bachatas</a></li>
                    <li><a href="{prefix}schedule.html">Stundenplan</a></li>
                    <li><a href="{prefix}blog.html">Unser Blog</a></li>

                </ul>
            </div>

            <div class="footer-col">
                <h2 class="footer-heading">Rechtliches</h2>
                <ul class="footer-links">
                    <li><a href="{prefix}terms.html">AGB</a></li>
                    <li><a href="{prefix}privacy.html">Datenschutz</a></li>
                    <li><a href="{prefix}imprint.html">Impressum</a></li>
                </ul>
            </div>
        </div>

        <div class="container footer-map-full" style="margin-bottom: 2rem;">
            <h2 class="footer-heading" style="margin-bottom: 1rem;">Finde uns</h2>
            <div class="footer-map-wrapper-large"
                style="border-radius: 12px; overflow: hidden; border: 1px solid var(--glass-border);">
                <iframe title="Google Maps Standort von AXcent Dance"
                    src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2701.567677685764!2d8.4844443!3d47.3861111!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47900a3910000001%3A0x1234567890abcdef!2sHermetschloostrasse%2073%2C%208048%20Z%C3%BCrich!5e0!3m2!1sen!2sch!4v1625000000000!5m2!1sen!2sch&hl=de"
                    width="100%" height="250" style="border:0; width: 100%; display: block;" allowfullscreen=""
                    loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 AXcent Dance. Alle Rechte vorbehalten.</p>
        </div>
    </footer>"""

def get_prefix(filepath):
    """
    Returns the relative prefix (e.g., "", "../", "../../") needed to get back to 'de/' root.
    """
    rel_path = os.path.relpath(filepath, DE_DIR)
    depth = rel_path.count(os.sep)
    
    # If file is in de/, depth is 0. Prefix is "" (empty) because links in footer like "index.html" are correct.
    # If file is in de/blog-posts, depth is 1. Prefix is "../" because we need to go up one level to reach "index.html"
    
    if depth == 0:
        return ""
    else:
        return "../" * depth

def propagate_footer(filepath):
    # Skip registration.html itself to prevent accidental mutation (though it's the source)
    if filepath.endswith('de/registration.html'):
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find existing footer
    # Matches <footer ... > ... </footer> non-greedy across newlines
    footer_pattern = re.compile(r'<footer class="main-footer">.*?</footer>', re.DOTALL)
    
    match = footer_pattern.search(content)
    if match:
        prefix = get_prefix(filepath)
        # In the special case of 'blog-posts/roots-of-bachata.html', it's already in the folder 'blog-posts'.
        # But the link is defined as `blog-posts/roots-of-bachata.html` relative to root.
        # If we are in `de/`, link is `blog-posts/roots-of-bachata.html` (Correct)
        # If we are in `de/blog-posts/`, we are at depth 1. Prefix is `../`.
        # Link becomes `../blog-posts/roots-of-bachata.html`.
        # This goes up to `de/`, then down to `blog-posts/`. This is valid.
        
        # However, for `index.html`, prefix is `../`. Link becomes `../index.html`. 
        # From `de/blog-posts/`, `../index.html` is `de/index.html`. Correct.
        
        new_footer = FOOTER_TEMPLATE.format(prefix=prefix)
        
        new_content = content.replace(match.group(0), new_footer)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated footer in: {filepath}")
    else:
        print(f"Skipping {filepath}: No footer found.")

def main():
    for root, dirs, files in os.walk(DE_DIR):
        for file in files:
            if file.endswith(".html"):
                propagate_footer(os.path.join(root, file))

if __name__ == "__main__":
    main()
