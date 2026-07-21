---
name: Create New Blog Post
description: comprehensive workflow to create a new blog post in both English and German, ensuring identical structure, Clean URLs, and automatic sitemap updates.
---

# Create New Blog Post

This skill guides you through the end-to-end process of publishing a new blog post. It strictly enforces the project's **Design Aesthetics**, **"En-De Parity"**, and **"Clean URL"** strategy.

## 1. Validate the Topic (Before You Write)
Do not pick a topic on instinct alone — confirm there is actual demand and a real gap first.
1.  **Check for demand**: Look at Google Search Console (queries/impressions) for terms people already search for that the site doesn't rank well for, or use the GSC topic action reports if available. A well-written post for a term nobody searches loses to a rougher post targeting a real query.
2.  **Check for existing coverage**: Grep `blog/` and the site's course/guide pages for the topic. If it's already covered:
    *   **Different angle only**: proceed only if you can add a genuinely new angle (comparison, recap, deeper dive) — not a rehash.
    *   **Authority page exists** (e.g., a course or guide page already targets the transactional keyword): follow the **Anti-Cannibalization Check** below instead of duplicating it.
3.  **State the target query**: Before writing, write down the one primary search query this post should win, plus 2-3 secondary long-tail variants. Every H2 and the meta description should trace back to these.

## 2. Gather Requirements
Ask the user for (or generate based on topic):
1.  **Slug**: The Clean URL part (e.g., `roots-of-bachata`).
2.  **Title (EN & DE)**: The H1 heading for both languages.
3.  **Description (EN & DE)**: The meta description (~150 chars).
4.  **Date**: `YYYY-MM-DDTHH:MM:SS+OFFSET` (ISO 8601).
    *   **Winter (CET)**: `+01:00` (e.g., `2025-12-07T12:00:00+01:00`)
    *   **Summer (CEST)**: `+02:00` (e.g., `2026-03-31T12:00:00+02:00`)
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

## 3. Generate HTML Files
You must create **two** files:
*   `blog/[slug].html` (English)
*   `de/blog/[slug].html` (German)

> Note: `blog-posts/` and `de/blog-posts/` are the RETIRED pre-migration locations. They contain only noindex redirect stubs — never create new posts there.

### **CRITICAL Rules for HTML Generation:**
1.  **Header & Footer**: MUST be practically identical to `index.html`. Update relative links (e.g., `href="../about"`).
2.  **Hreflang Tags**: MUST exist and cross-reference each other.
3.  **Canonical**: MUST point to the clean URL (NO `.html`).
4.  **Clean Links**: All internal links must NOT have `.html`.
5.  **Schema & Breadcrumb Requirements**: MUST include `BreadcrumbList` schema in the `<head>`. Visual breadcrumbs are NOT required.
    *   Level 1: Home (`/`)
    *   Level 2: Blog (`/blog`)
    *   Level 3: Post Title (`/blog/[slug]`)
6.  **Schema Specifics (Mandatory)**: 
    *   **inLanguage**: MUST include `"inLanguage": "en"` (for English posts) or `"inLanguage": "de"` (for German posts) in both the `WebPage` and `BlogPosting` entities. 
    *   **Author**: MUST use the dual Person `@id` reference pattern (`[{"@id": "...#person1"}, {"@id": "...#person2"}]`).
    *   **Image**: MUST use `ImageObject` with `width` and `height` properties, not a plain URL string.
7.  **Schema Synchronization**: Whenever any factual information (Dates, Artists, Locations, etc.) is changed on a page, you MUST check and update the corresponding JSON-LD Schema to ensure it remains accurate and is not contradicting what is shown to the user. **All timestamped dates (`datePublished`, `startDate`, etc.) MUST include time and UTC offset (ISO 8601); `dateModified` uses date-only `YYYY-MM-DD` (managed by `scripts/sync_blog_dates.py`).**
8.  **Automation**: After creating the HTML files, run the update scripts. These scripts handle internal link cleanup, image optimization discovery, and SEO date synchronization.
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

### **Optional: GSAP / Three.js Visualization**
Only reach for this if the post has a concept that a static image genuinely cannot explain — a technique that unfolds over time, a spatial relationship, a comparison, a piece of data. If the post works fine with photos and text, skip this section entirely.

1.  **Bar for inclusion — it must explain something real**:
    *   Good: animating the frame/lead-follow mechanics in `dance-tips-1-frame.html`-style content, an interactive timeline of bachata's evolution for `roots-of-bachata`-style content, a step-count/tempo comparison chart for a musicality post, a before/after or side-by-side for a styling post.
    *   Bad: floating abstract particles, generic gradient blobs, decorative "hero" shapes with no label or purpose, anything you'd struggle to caption in one sentence. If you can't explain in the alt/caption what the visualization *shows*, don't build it.
    *   When in doubt, ask: does this help the reader understand or decide something, or is it just motion for motion's sake? Only build it if the former.
2.  **GSAP** (already used site-wide, e.g. `index.html`, `dominican-bootcamp.html`, `events.html`): use for scroll-triggered reveals, sequencing a step-by-step explanation, or animating a real data comparison (e.g., counting up a stat). Load the same version already in use:
    ```html
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
    ```
    Register `ScrollTrigger` only if the animation is tied to scroll position; otherwise a plain `gsap.to()`/timeline on load is enough — don't add the plugin for a one-shot animation.
3.  **Three.js**: not currently used anywhere on the site — treat it as a heavier, rarer tool. Only justified for a genuinely spatial concept (e.g., visualizing partner rotation/frame in 3D, a floor-pattern diagram for a choreography post). Reserve for a post where 2D truly can't communicate the idea, and confirm with the user before adding a new dependency to the stack.
4.  **Performance & accessibility guardrails**:
    *   Must not block or delay the LCP image or main content — defer/lazy-init the visualization.
    *   Provide a static fallback (image or plain text) for users with `prefers-reduced-motion` or JS disabled — the post must be fully readable without it.
    *   Keep it out of the hero/above-the-fold if it risks hurting Core Web Vitals; place it deeper in the post where it supports a specific paragraph.

### **Image Optimization Rules (Simple & Good Defaults)**
1.  **Format**: MUST be **WebP** only.
2.  **Size**: **1200px wide maximum**. Target file size between **60-80KB**.
3.  **No `srcset`**: Complex `srcset` or `sizes` attributes are NOT required.
4.  **Alt Text**: Mandatory and descriptive for every single image.
5.  **Dimensions**: Explicit `width` and `height` attributes to prevent CLS.
6.  **Lazy Loading**: Use `loading="lazy"` for all images except the first LCP candidate.

## 4. Update Main Blog Page (`blog/index.html` and `de/blog/index.html`)
You must link the new post on the main blog listing page.
1.  **Placement**: Sort by date (Newest First).
2.  **Category**: Set `data-category` on the card to one of the existing filter values: `music`, `tips`, `community`, `education`, `wellness`, or `events` — the visible `.card-category` badge text should match the filter it belongs to.
3.  **Card Format**: Use the existing card structure (`.modern-card`).
    *   Include Thumbnail (WebP).
    *   Include Title & Short Excerpt.
    *   Link to the *Clean URL*.

## 5. Update Site Indexing & AI Context
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
    <loc>https://axcentdance.com/blog/[SLUG]</loc>
    <lastmod>[YYYY-MM-DD]</lastmod>
    <priority>0.7</priority>
    <xhtml:link rel="alternate" hreflang="en" href="https://axcentdance.com/blog/[SLUG]" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://axcentdance.com/blog/[SLUG]" />
    <xhtml:link rel="alternate" hreflang="de" href="https://axcentdance.com/de/blog/[SLUG]" />
    <image:image>
      <image:loc>https://axcentdance.com/[IMAGE_PATH]</image:loc>
      <image:title>[TITLE_EN_ESCAPED]</image:title>
    </image:image>
  </url>
```
*(Repeat structure for German block with `/de/` links and localized titles)*

## 6. Post-Publish: Get It Discovered
A page with zero inbound links and no follow-up is unlikely to get crawled or ranked promptly. Do not stop at publishing.
1.  **Link into it from existing pages**: Add at least 1-2 contextual links to the new post from relevant existing pages (related blog posts, the course/guide page it supports, or the homepage if highly relevant). New pages get discovered through internal links, not just the sitemap.
2.  **Cross-link related posts**: If older posts cover an adjacent topic, add a short "related reading" link to the new post from them (and vice versa) rather than leaving the new post as an island.
3.  **Check back in Search Console**: 2-3 weeks after publishing, check GSC for the target query from Section 1 — is the post getting impressions? Ranking near page 1-3? If it's flat, revisit the title/H1/meta description before writing something new.

## 7. Verification
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



