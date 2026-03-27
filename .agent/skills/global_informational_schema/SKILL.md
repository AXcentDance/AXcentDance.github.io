---
name: Global Informational Schema
description: Guidelines on how to structure JSON-LD schema for global informational pages (like guides and educational articles) to prevent them from being penalized by local business constraints.
---

# Global Informational Schema Guidelines

When creating or modifying pages that target global or broad informational queries—such as encyclopedic guides, history deep-dives, or educational resources (e.g., `/education.html`, `/guide-bachata.html`)—you must apply specific schema guidelines to prevent Google from restricting the page's reach to purely local searchers.

## The Problem (Local Override)
According to Project Rule 5.2, every page on AXcent Dance MUST include the `LocalBusiness` (`DanceSchool`) and founders (`#person1`, `#person2`) entities within its `@graph`. 

While this builds massive domain authority, putting a heavy `LocalBusiness` schema (which includes Zurich coordinates, street addresses, and prices) onto an informational page confuses search engines. If the `LocalBusiness` is the most definitive entity on the page, Google assumes the page is a commercial landing page meant *only* for locals. This causes massive drops in global impressions.

## The Solution: Explicit `mainEntity` Binding
To resolve this conflict, you must inject an `Article` object into the `@graph` and forcefully declare it as the primary focus of the page. This tells Google: *"Yes, we are a local business publisher, but the core intent of this specific page is a globally relevant informational article."*

### Step 1: Add `mainEntity` to the `WebPage` Definition
Locate the `WebPage` object inside the page's JSON-LD `@graph`. You must add the `"mainEntity"` property, pointing directly to the `@id` of the article:

```json
{
  "@type": "WebPage",
  "@id": "https://axcentdance.com/example-guide#webpage",
  "url": "https://axcentdance.com/example-guide",
  "name": "Example Guide Title | AXcent Dance",
  "isPartOf": { "@id": "https://axcentdance.com/#website" },
  "description": "...",
  "mainEntity": {
    "@id": "https://axcentdance.com/example-guide#article"
  }
}
```

### Step 2: Inject a Robust `Article` Object
If the `@graph` does not already contain an `Article` object, create one. It MUST include `mainEntityOfPage`, `author`, and `publisher` to seamlessly connect with the global site identity.

```json
{
  "@type": "Article",
  "@id": "https://axcentdance.com/example-guide#article",
  "inLanguage": "en",
  "headline": "Example Guide Title",
  "datePublished": "2025-01-01",
  "dateModified": "YYYY-MM-DD",
  "author": [
    { "@id": "https://axcentdance.com/#person1" },
    { "@id": "https://axcentdance.com/#person2" }
  ],
  "publisher": {
    "@id": "https://axcentdance.com/#organization"
  },
  "description": "A robust, informative description.",
  "image": {
    "@type": "ImageObject",
    "url": "https://axcentdance.com/assets/images/hero-image.webp",
    "width": 1200,
    "height": 675
  },
  "mainEntityOfPage": {
    "@id": "https://axcentdance.com/example-guide#webpage"
  }
}
```

### Key Takeaways
- **Never Replace `LocalBusiness`:** Leave the `DanceSchool` schema intact at the bottom of the `@graph`. 
- **Two-Way Linking:** The `WebPage` must point to the `Article` via `"mainEntity"`, and the `Article` must point back to the `WebPage` via `"mainEntityOfPage"`.
- **Image Requirements:** All `Article` and `BlogPosting` objects ideally require a 1200px wide image to trigger Google Discover cards.
