---
name: Unified Schema Management
description: Mandatory guidelines for maintaining a single JSON-LD @graph structure across all pages, ensuring data consistency and preventing redundant schema scripts.
---

# Unified Schema Management

This skill enforces the use of a single, coherent JSON-LD `@graph` structure for all structured data. To maximize SEO efficiency and prevent data fragmentation, **NEVER** use standalone `<script type="application/ld+json">` blocks for separate entities (like Breadcrumbs or FAQs) if they can be integrated into the main page graph.

## 1. Core Principles
1.  **Single Source of Truth**: Every page MUST have exactly one main JSON-LD script containing a `@graph` array.
2.  **Entity Linking**: Use `@id` references (e.g., `https://axcentdance.com/#organization`) to link entities across different pages and within the same graph.
3.  **No Redundancy**: If a property (like `LocalBusiness`) is already defined in the graph, do not create a separate script for it elsewhere on the page.

## 2. Mandatory @graph Structure
Your JSON-LD block must follow this pattern:

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
      "@type": "LocalBusiness",
      "@id": "https://axcentdance.com/#organization",
      "name": "AXcent Dance",
      "url": "https://axcentdance.com/",
      "telephone": "+41799668481",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "Hermetschloostrasse 73",
        "addressLocality": "Zurich",
        "postalCode": "8048",
        "addressCountry": "CH"
      }
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://axcentdance.com/[page-path]#breadcrumb",
      "itemListElement": [ ... ]
    },
    /* Add page-specific types here: FAQPage, Course, BlogPosting, etc. */
  ]
}
</script>
```

## 3. Page-Specific Entities
*   **Blog Posts**: Include `BlogPosting` and `VideoObject` (if applicable) within the graph. Link them to the `WebPage` via `mainEntityOfPage`.
*   **Schedule Page**: Include `ItemList` containing detailed `Course` objects (with `offers`, `instructor`, and `CourseInstance`).
*   **FAQ Sections**: Include `FAQPage` within the graph, linked to the `WebPage` via `isPartOf`.

## 4. Internationalization (EN-DE Parity)
*   **German Pages**: All `name`, `description`, and `itemListElement` labels within the schema MUST be in German.
*   **IDs**: Keep `@id` URLs consistent (use the `/de/` path for the `WebPage` and `BreadcrumbList` IDs).

## 5. Workflow for Modifications
1.  **Audit**: Check for existing standalone `<script>` blocks (search for `BreadcrumbList` and `FAQPage`).
2.  **Consolidate**: Extract the data from standalone blocks and merge them into the `@graph` array.
3.  **Delete**: Remove the original standalone scripts to prevent "Duplicate Schema" warnings in Google Search Console.
4.  **Validate**: Run the `seo_audit.py` to ensure titles and descriptions match the schema.
