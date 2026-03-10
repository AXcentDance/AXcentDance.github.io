---
name: Create New Blog Post
description: comprehensive workflow to create a new blog post in both English and German, ensuring identical structure, Clean URLs, and automatic sitemap updates.
---

# Create New Blog Post

This skill guides you through the end-to-end process of publishing a new blog post. It strictly enforces the project's **Design Aesthetics**, **"En-De Parity"**, and **"Clean URL"** strategy.

## 1. Gather Requirements
Ask the user for (or generate based on topic):
1.  **Slug**: The Clean URL part (e.g., `roots-of-bachata`).
2.  **Title (EN & DE)**: The H1 heading for both languages.
3.  **Description (EN & DE)**: The meta description (~150 chars).
4.  **Date**: `YYYY-MM-DD`.
5.  **Images**:
    *   **Hero Image**: Absolute path (e.g., `assets/images/blog/hero.webp`).
    *   **Body Images**: **At least 2 additional images** relevant to the content.
6.  **Content Strategy**:
    *   **Tone**: Catchy but serious. Relevant and relatable. Avoid generic fluff.
    *   **Structure**: Must include "interesting formatting" (grids, highlights, quotes), not just text.
    *   **Internal Linking**: MUST include **2-4 contextual internal links** within the body text (e.g., linking to `schedule`, `registration`, or `beginner-guide`). Use descriptive anchor text; do NOT use "click here". Links must be woven naturally into the content.
    *   **Anti-Cannibalization Check**: If the post's topic is already the primary SEO objective of another "Authority" page (e.g., an Event landing page like `dominican-bootcamp`), you MUST:
        1.  **Differentiate Intent**: Change the blog's Title/H1 to be Informational (e.g., "What to expect at...", "Behind the scenes", "Recap") rather than Transactional.
        2.  **Preserve Authority**: Include a link in the first paragraph using the target "Head Keyword" as anchor text pointing to the Authority page.

## 2. Generate HTML Files
You must create **two** files:
*   `blog-posts/[slug].html` (English)
*   `de/blog-posts/[slug].html` (German)

### **CRITICAL Rules for HTML Generation:**
1.  **Header & Footer**: MUST be practically identical to `index.html`. Update relative links (e.g., `href="../about"`).
2.  **Hreflang Tags**: MUST exist and cross-reference each other.
3.  **Canonical**: MUST point to the clean URL (NO `.html`).
4.  **Clean Links**: All internal links must NOT have `.html`.
3.  **Schema & Breadcrumb Requirements**: MUST include `BreadcrumbList` schema in the `<head>`. Visual breadcrumbs are NOT required.
    *   Level 1: Home (`/`)
    *   Level 2: Blog (`/blog`)
    *   Level 3: Post Title (`/blog-posts/[slug]`)
4.  **Schema Synchronization**: Whenever any factual information (Dates, Artists, Locations, etc.) is changed on a page, you MUST check and update the corresponding JSON-LD Schema to ensure it remains accurate and is not contradicting what is shown to the user.
4.  **Automation**: After creating the HTML files, run the update scripts. These scripts handle internal link cleanup, image optimization discovery, and SEO date synchronization.
    ```bash
    # 1. Sync dateModified with file timestamp
    python3 scripts/sync_blog_dates.py

    # 2. Inject/Update Breadcrumb Schema (JSON-LD)
    python3 scripts/inject_breadcrumb_schema.py

    # 3. Audit Breadcrumb Schema (Head ONLY)
    python3 scripts/breadcrumb_audit.py

    # 4. Update LLM context (llms-full.txt)
    python3 scripts/generate_llms_txt.py
    ```

### **Design & Layout Requirements (Mandatory)**
Do NOT create a "Wall of Text". You must use the following CSS components from `blog-post.css`:

1.  **Hero Section**:
    *   Use `.post-hero` with the background image.
    *   Include metadata badge: `<span class="badge badge--education">Category</span>`.

2.  **Visual Breakpoints (Min 2)**:
    *   Insert images using `.post-hero-image` (rounded corners, shadow) or `.collage-section`.
    *   Use `<figcaption>` for image captions.

3.  **Interesting Formatting (Choose at least one)**:
    *   **Bento Grid**: Use `.bento-grid` with `.bento-card` for listing features, tips, or steps.
    *   **Highlight Box**: Use `.bento-card.highlight-card` for key takeaways.
    *   **FAQ Section**: Use `.faq-section` (from `style.css`) for Q&A style content.

### **Image Optimization Rules (Simple & Good Defaults)**
1.  **Format**: MUST be **WebP** only.
2.  **Size**: **1200px wide maximum**. Target file size between **60-80KB**.
3.  **No `srcset`**: Complex `srcset` or `sizes` attributes are NOT required.
4.  **Alt Text**: Mandatory and descriptive for every single image.
5.  **Dimensions**: Explicit `width` and `height` attributes to prevent CLS.
6.  **Lazy Loading**: Use `loading="lazy"` for all images except the first LCP candidate.

## 3. Update Main Blog Page (`blog.html` and `de/blog.html`)
You must link the new post on the main blog listing page.
1.  **Placement**: Sort by date (Newest First).
2.  **Category**: Place it under the correct category filter: `Music`, `Dance Tips`, `Community`, `Education`, `Wellness`, or `Events`.
3.  **Card Format**: Use the existing card structure (`.blog-card`).
    *   Include Thumbnail (WebP).
    *   Include Title & Short Excerpt.
    *   Link to the *Clean URL*.

## 4. Update Site Indexing & AI Context (Final Step)
**After** any new page is created or content is modified, you MUST update both the search engine index (sitemap) and the AI crawler context (llms-full.txt). These are the two primary ways the site is discovered by both humans and LLMs.

### Automated Synchronization (Recommended)
Run these two scripts to ensure everything is synchronized correctly:

```bash
# 1. Update Sitemap (XML for Search Engines)
python3 scripts/generate_sitemap_final.py

# 2. Update LLM context (llms-full.txt for AI Crawlers)
python3 scripts/generate_llms_txt.py
```

### Technical Note
*   The Sitemap generator handles Clean URLs, hreflang tags, and escapes special characters (e.g., `&` becomes `&amp;`).
*   The LLM generator (llms-full.txt) strips scripts/styles and provides a clean, text-only feed of all pages for RAG systems.

### Option B: Manual Update
If you must update manually, insert the new URLs before `</urlset>`. 

**CRITICAL: You MUST escape special characters in `<image:title>` (e.g., `&` becomes `&amp;`, `<` becomes `&lt;`). Failure to do this will break the sitemap parsing.**

**English Block:**
```xml
  <url>
    <loc>https://axcentdance.com/blog-posts/[SLUG]</loc>
    <lastmod>[YYYY-MM-DD]</lastmod>
    <priority>0.7</priority>
    <xhtml:link rel="alternate" hreflang="en" href="https://axcentdance.com/blog-posts/[SLUG]" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://axcentdance.com/blog-posts/[SLUG]" />
    <xhtml:link rel="alternate" hreflang="de" href="https://axcentdance.com/de/blog-posts/[SLUG]" />
    <image:image>
      <image:loc>https://axcentdance.com/[IMAGE_PATH]</image:loc>
      <image:title>[TITLE_EN_ESCAPED]</image:title>
    </image:image>
  </url>
```
*(Repeat structure for German block with `/de/` links and localized titles)*

## 5. Verification
1.  **Sitemap Validation**: Run a quick check to ensure the XML is well-formed.
    ```bash
    python3 -c "import xml.etree.ElementTree as ET; ET.parse('sitemap.xml')"
    ```
2.  **Design Check**: Does the page look premium? Are there 2+ images in the body? Is the text broken up by grids/cards?
3.  **Technical Check**: 
    *   Clean URLs and correct Hreflangs?
    *   `sitemap.xml` contains no bare `&` characters?
    *   `dateModified` in schema match current date? (Run `python3 scripts/sync_blog_dates.py`)
    *   Breadcrumb Schema injected and valid? (Run `python3 scripts/inject_breadcrumb_schema.py` then `python3 scripts/breadcrumb_audit.py`)
    *   `llms-full.txt` updated with new content? (Run `python3 scripts/generate_llms_txt.py`)



