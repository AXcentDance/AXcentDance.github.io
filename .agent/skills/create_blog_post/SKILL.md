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
    *   **Tone**: Catchy but serious. Relevant and relatable. avoid generic fluff.
    *   **Structure**: Must include "interesting formatting" (grids, highlights, quotes), not just text.

## 2. Generate HTML Files
You must create **two** files:
*   `blog-posts/[slug].html` (English)
*   `de/blog-posts/[slug].html` (German)

### **CRITICAL Rules for HTML Generation:**
1.  **Header & Footer**: MUST be practically identical to `index.html`. Update relative links (e.g., `href="../about"`).
2.  **Hreflang Tags**: MUST exist and cross-reference each other.
3.  **Canonical**: MUST point to the clean URL (NO `.html`).
4.  **Clean Links**: All internal links must NOT have `.html`.
5.  **Schema Markup**: MUST include `BreadcrumbList` schema.
    *   Level 1: Home (`/`)
    *   Level 2: Blog (`/blog`)
    *   Level 3: Post Title (`/blog-posts/[slug]`)

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

### **Image Optimization Rules (Strict)**
1.  **Format**: MUST be `.webp` only.
2.  **Responsiveness**: MUST use `srcset` for all images (Hero & Body).
    *   Example: `srcset="image_480w.webp 480w, image_800w.webp 800w, image_1200w.webp 1200w"`
    *   Sizes: `sizes="(max-width: 600px) 480px, (max-width: 900px) 800px, 1200px"`
3.  **Alt Text**: Mandatory and descriptive for every single image.
4.  **Dimensions**: Explicit `width` and `height` attributes to prevent CLS.

## 3. Update Main Blog Page (`blog.html` and `de/blog.html`)
You must link the new post on the main blog listing page.
1.  **Placement**: Sort by date (Newest First).
2.  **Category**: Place it under the correct category filter: `Music`, `Dance Tips`, `Community`, `Education`, `Wellness`, or `Events`.
3.  **Card Format**: Use the existing card structure (`.blog-card`).
    *   Include Thumbnail (WebP).
    *   Include Title & Short Excerpt.
    *   Link to the *Clean URL*.

## 4. Update Sitemap (Final Step)
**After** the files are created and verified, you MUST add them to `sitemap.xml`.

### Snippets to Append (Insert before `</urlset>`)
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
      <image:title>[TITLE_EN]</image:title>
    </image:image>
  </url>
```
*(Repeat structure for German block with `/de/` links)*

## 4. Verification
1.  **Design Check**: Does the page look premium? Are there 2+ images in the body? Is the text broken up by grids/cards?
2.  **Technical Check**: Clean URLs? Hreflangs correct? Sitemap updated?


