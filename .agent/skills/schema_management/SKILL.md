---
name: Unified Schema Management
description: Mandatory guidelines for maintaining a single JSON-LD @graph structure across all pages, ensuring data consistency and preventing redundant schema scripts.
---

# Unified Static Schema Management

This skill enforces the use of a single, coherent JSON-LD `@graph` structure for all structured data, embedded directly in the HTML. **NEVER** use standalone `<script type="application/ld+json">` blocks or external JavaScript (like `schema.js`) to inject structured data.

## 1. Core Principles
1.  **Single Source of Truth**: Every page MUST have exactly one main JSON-LD script containing a `@graph` array in the `<head>`.
2.  **Entity Linking**: Use `@id` references (e.g., `https://axcentdance.com/#organization`) to link entities.
3.  **Static Execution**: All schema must be readable in the raw HTML without JavaScript execution to optimize for AI Crawlers (Gemini, ChatGPT) and search engine speed.
4.  **Global Entities**: Every `@graph` should include the foundational entities (`Organization`/`DanceSchool` and `Person` for Ale & Xidan) to ensure self-contained authority on every page.

## 2. Mandatory @graph Structure Template
Your JSON-LD block must follow this pattern exactly:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebPage",
      "@id": "https://axcentdance.com/[page-path]#webpage",
      "url": "https://axcentdance.com/[page-path]",
      "name": "[Page Title]",
      "isPartOf": { "@id": "https://axcentdance.com/#website" },
      "inLanguage": "[en/de]",
      "description": "[Meta Description]"
    },
    {
      "@type": "WebSite",
      "@id": "https://axcentdance.com/#website",
      "url": "https://axcentdance.com/",
      "name": "AXcent Dance",
      "publisher": { "@id": "https://axcentdance.com/#organization" }
    },
    {
      "@type": ["LocalBusiness", "DanceSchool"],
      "@id": "https://axcentdance.com/#organization",
      "name": "AXcent Dance",
      "url": "https://axcentdance.com/",
      "logo": "https://axcentdance.com/assets/images/logo.webp",
      "image": "https://axcentdance.com/assets/images/hero_new.webp",
      "priceRange": "$$",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "Hermetschloostrasse 73",
        "addressLocality": "Zurich",
        "postalCode": "8048",
        "addressCountry": "CH"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 47.3941999,
        "longitude": 8.4745859
      }
    },
    {
      "@type": "Person",
      "@id": "https://axcentdance.com/#person1",
      "name": "Alessandro Slamitz",
      "jobTitle": "Co-Founder",
      "sameAs": ["https://www.instagram.com/aleyxidan/"]
    },
    {
      "@type": "Person",
      "@id": "https://axcentdance.com/#person2",
      "name": "Xidan",
      "jobTitle": "Co-Founder",
      "sameAs": ["https://www.instagram.com/aleyxidan/"]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://axcentdance.com/[page-path]#breadcrumb",
      "itemListElement": [ ... ]
    }
    /* Add page-specific types here: BlogPosting, Event, etc. */
  ]
}
</script>
```

## 3. Page-Specific Entities
*   **Blog Posts**: Include `BlogPosting` within the graph. Use `author` array pointing to `[{"@id": "...#person1"}, {"@id": "...#person2"}]`.
*   **FAQ Sections**: Include `FAQPage` within the graph, linked to the `WebPage`.


## 4. Internationalization (EN-DE Parity)
*   **German Pages**: All `name`, `description`, and `itemListElement` labels within the schema MUST be in German.
*   **IDs**: Keep `@id` URLs consistent (use the `/de/` path for the `WebPage` and `BreadcrumbList` IDs).

## 5. Workflow for Modifications
1.  **Audit**: Check for existing standalone `<script>` blocks (search for `BreadcrumbList` and `FAQPage`).
2.  **Consolidate**: Extract the data from standalone blocks and merge them into the `@graph` array.
3.  **Delete**: Remove the original standalone scripts to prevent "Duplicate Schema" warnings in Google Search Console.
4.  **Validate**: Run the `seo_audit.py` to ensure titles and descriptions match the schema.
