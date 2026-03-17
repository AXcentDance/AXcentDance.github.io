---
name: Geo-Tagging & Local SEO Injection
description: Comprehensive workflow to inject high-authority local SEO markers (coordinates, CID, maps) into new pages and blog posts for AXcent Dance Zurich.
---

# Geo-Tagging & Local SEO Injection

This skill ensures that every new page or blog post created for AXcent Dance is mathematically "locked" to the physical studio location in Zurich Altstetten. This improves visibility in the Google "Map Pack" and helps AI crawlers citation accuracy.

## 1. Master Location Data (Sources of Truth)
Always use these exact values. Do not approximate.

- **Address**: Hermetschloostrasse 73, 8048 Zurich, Switzerland
- **Latitude**: `47.3941999`
- **Longitude**: `8.4745859`
- **Google CID**: `15680757943659417558`
- **Google Maps Link**: `https://www.google.com/maps?cid=15680757943659417558`

## 2. Schema.org Implementation

### A. LocalBusiness Injection
Every new landing page or service page SHOULD include a linked `LocalBusiness` bridge in the `<head>` schema.

```json
{
  "@type": "LocalBusiness",
  "@id": "https://axcentdance.com/#organization",
  "name": "AXcent Dance",
  "url": "https://axcentdance.com/",
  "hasMap": "https://www.google.com/maps?cid=15680757943659417558",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 47.3941999,
    "longitude": 8.4745859
  },
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Hermetschloostrasse 73",
    "addressLocality": "Zurich",
    "addressRegion": "ZH",
    "postalCode": "8048",
    "addressCountry": "CH"
  }
}
```

### B. Blog Post Location Tagging
For blog posts (`BlogPosting`), add the `contentLocation` property to signal where the story or expertise originates.

```json
"contentLocation": {
  "@type": "Place",
  "name": "AXcent Dance Studio Zurich",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Hermetschloostrasse 73",
    "addressLocality": "Zurich",
    "postalCode": "8048",
    "addressCountry": "CH"
  }
}
```

## 3. Map Embed Protocols
When adding the footer or a location section, use the high-authority embed code.

### English Pages (EN)
`src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2701.365!2d8.472010!3d47.394204!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47900b995a7d8e03%3A0xd99d3e4500b44fd6!2sAXcent%20Dance%20%7C%20Bachata%20Classes!5e0!3m2!1sen!2sch!4v1710680000000!5m2!1sen!2sch&hl=en"`

### German Pages (DE)
`src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2701.365!2d8.472010!3d47.394204!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47900b995a7d8e03%3A0xd99d3e4500b44fd6!2sAXcent%20Dance%20%7C%20Bachata%20Classes!5e0!3m2!1sen!2sch!4v1710680000000!5m2!1sde!2sch&hl=de"`

## 4. Image Geo-Tagging Best Practices
When adding new hero images:
1. Ensure the `alt` text includes a local modifier (e.g., "Bachata classes at AXcent Dance Zurich Altstetten").
2. **Pro Tip**: If possible, suggest to the USER to ensure the original JPEG/WebP files exported from their camera or editor contain the GPS EXIF data matching the studio coordinates.

## 5. Verification Checklist
- [ ] Schema contains `hasMap` with CID `15680757943659417558`.
- [ ] `GeoCoordinates` are exactly `47.3941999` (Lat) and `8.4745859` (Long).
- [ ] Map `<iframe>` title and `src` point to the specific business entity, not just a street address.
