import os
import re

    # 4. Save if changed
    if content_before != new_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed/Updated: {file_path}")

def main():
    root_dir = '/Users/slamitza/AXcentWebsiteGitHub'
    
    def process_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()
        
        # Add Language Switcher (if missing)
        content = original
        if 'class="lang-switch"' not in content:
            filename = os.path.basename(file_path)
            if 'blog-posts' in file_path:
                de_link = f'de/blog-posts/{filename}'
            elif filename == 'index.html':
                de_link = 'de/'
            else:
                de_link = f'de/{filename}'
                
            switcher = f'''                <div class="lang-switch"
                    style="display: inline-flex; gap: 6px; margin-left: 10px; margin-right: 10px; align-items: center; font-weight: 500; font-size: 0.95rem;">
                    <span
                        style="color: white; border-bottom: 2px solid var(--accent-start); padding-bottom: 2px;">EN</span>
                    <span style="color: rgba(255,255,255,0.4);">|</span>
                    <a href="{de_link}"
                        style="color: rgba(255,255,255,0.7); text-decoration: none; transition: color 0.2s;">DE</a>
                </div>
'''
            cta_match = re.search(r' {12,16}<a href=".*?" class="btn-header-cta">', content)
            if cta_match:
                insert_pos = cta_match.start()
                content = content[:insert_pos] + switcher + content[insert_pos:]
        
        # Ensure Logo Link points to English root
        content = re.sub(r'<a href="(/de/|de/)" class="logo">', r'<a href="/" class="logo">', content)
        
        # Ensure CTA Link points to English root (trial form)
        content = content.replace('href="/de/#trial-form"', 'href="/#trial-form"')

        if original != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
    pages = [
        'about.html', 'beginner-guide.html', 'blog.html', 'contact.html',
        'corporate-events.html', 'education.html', 'etiquette.html', 'events.html',
        'faq.html', 'gallery.html', 'imprint.html', 'privacy.html',
        'private-lessons.html', 'registration.html', 'room-rental.html',
        'schedule.html', 'terms.html', 'wedding-dance.html', 'guide-social-dancing.html'
    ]
    
    for page in pages:
        path = os.path.join(root_dir, page)
        if os.path.exists(path):
            fix_links_in_file(path)
            
    blog_posts_dir = os.path.join(root_dir, 'blog-posts')
    for file in os.listdir(blog_posts_dir):
        if file.endswith('.html'):
            fix_links_in_file(os.path.join(blog_posts_dir, file))

if __name__ == "__main__":
    main()
