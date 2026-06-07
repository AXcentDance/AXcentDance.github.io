---
description: Correct image schema pattern for BlogPosting, Article, and Event structured data on AXcent Dance
---

# Image & Author Schema Standards for AXcent Dance

Use this skill whenever you add or update an `image` or `author` property inside any JSON-LD schema block (`BlogPosting`, `Article`, `Event`, `EventSeries`, etc.).

---

## ✅ Is ImageObject Still the Correct Standard?

**Yes — confirmed by Google's official documentation (March 2026).**

Google's [Article structured data spec](https://developers.google.com/search/docs/appearance/structured-data/article) defines `image` as:

> **Repeated `ImageObject` or `URL`**

A plain URL string is *technically valid*, but **`ImageObject` with explicit `width` and `height` is strongly preferred** because:

1. **Google Discover large image cards** require images ≥ 1200px wide. Providing dimensions lets Google instantly validate eligibility without downloading the image.
2. **Rich result ranking signals** — Google explicitly recommends providing multiple aspect ratios (16:9, 4:3, 1:1). With `ImageObject` you can do this precisely.
3. **CrUX / performance signals** — width/height prevent layout shift which directly affects Core Web Vitals scoring.

---

## The Correct Pattern

### Single image (most blog posts)

```json
"image": {
  "@type": "ImageObject",
  "url": "https://axcentdance.com/assets/images/blog/YOUR-IMAGE.webp",
  "width": 1200,
  "height": 675
}
```

### Multiple aspect ratios (ideal for Google Discover — flagship posts only)

```json
"image": [
  {
    "@type": "ImageObject",
    "url": "https://axcentdance.com/assets/images/blog/hero_16x9.webp",
    "width": 1200,
    "height": 675
  },
  {
    "@type": "ImageObject",
    "url": "https://axcentdance.com/assets/images/blog/hero_4x3.webp",
    "width": 1200,
    "height": 900
  },
  {
    "@type": "ImageObject",
    "url": "https://axcentdance.com/assets/images/blog/hero_1x1.webp",
    "width": 1200,
    "height": 1200
  }
]
```

### Event pages (arrays of plain URLs are fine here)

```json
"image": [
  "https://axcentdance.com/assets/images/MilanoSensualCongress2026.webp"
]
```

> **Note:** For `Event` schema, Google accepts a plain URL array. `ImageObject` is still allowed but unnecessary.

---

## Mandatory Rules

1. **Always use absolute `https://axcentdance.com/...` URLs** — never relative paths.
2. **Always get real dimensions** before writing the schema. Use:
   ```bash
   python3 -c "from PIL import Image; im=Image.open('assets/images/blog/YOUR.webp'); print(im.size)"
   ```
   Run from the site root: `/Users/slamitza/AXcentWebsiteGitHub`
3. **Minimum size for Discover eligibility:** width ≥ 1200px and height ≥ 675px (16:9). Images below this threshold will not get large Discover cards.
4. **Format must be WebP** — all blog images are already WebP per project rules.
5. **The `image` URL must be the same as (or a crop of) the hero image visible on the page** — Google penalises schema images that don't match visible content.

---

## Known Image Dimensions (Site Reference)

| File | Width | Height | Aspect |
|---|---|---|---|
| `blog/burkliplatz_night.webp` | 1024 | 692 | ~3:2 |
| `hero_new.webp` | 1024 | 768 | 4:3 |
| `christmas_break_2025.webp` | 1024 | 1024 | 1:1 |
| `blog/connection-101.webp` | 1024 | 1024 | 1:1 |
| `dominican_bootcamp.webp` | 819 | 1024 | portrait |
| `blog/first-week-new-studio.webp` | 1024 | 768 | 4:3 |
| `gallery/gallery_1.webp` | 1024 | 576 | 16:9 |
| `blog/latin_school_hero.webp` | 1024 | 1024 | 1:1 |
| `studio/studio_room_view_1.webp` | 1024 | 651 | ~16:10 |
| `romeo_santos.webp` | 1024 | 1024 | 1:1 |
| `blog/romeo-prince-tour-2026.webp` | 838 | 1024 | portrait |
| `blog/roots-of-bachata-hero.webp` | 1200 | 1200 | 1:1 ✅ Discover Ready |
| `blog/science-of-dance-mental-health.webp` | 1024 | 1024 | 1:1 |
| `blog/sensation-hero.webp` | 819 | 1024 | portrait |
| `blog/first-week-new-studio_1200w.webp` | 1200 | 900 | 4:3 ✅ |
| `bachata_essentials_flatlay.webp` | 1024 | 1024 | 1:1 |
| `blog/salsa_vs_bachata_hero.webp` | 1024 | 1024 | 1:1 |
| `MilanoSensualCongress2026.webp` | — | — | check with PIL |

> ⚠️ `roots-of-bachata-hero.webp` is only 640×640. It will **not** get a Google Discover large image card. Consider generating a 1200×675 version.

---

## Workflow When Adding a New Blog Post

When you create a new blog post (using the `create_blog_post` skill), follow this checklist for the `image` property:

1. Identify the hero image path (relative to site root).
2. Get its dimensions: `python3 -c "from PIL import Image; im=Image.open('PATH'); print(im.size)"`
3. Check if width ≥ 1200. If not, note it as a Discover limitation but still use the real dimensions.
4. Write the `ImageObject` block with those exact values.
5. Add the image to the Known Image Dimensions table above if it is new.

---

## Batch Upgrade Script

If you ever need to batch-upgrade plain URL strings to `ImageObject` across all blog posts, the upgrade script is at:

```
/tmp/upgrade_image_to_imageobject.py
```

Update `IMAGE_DIMS` at the top of the script with the new image before running.
Run from site root: `python3 /tmp/upgrade_image_to_imageobject.py`

---

## Author Schema Standard

### ✅ Canonical Pattern — Dual Person @id References

All `BlogPosting` schemas on AXcent Dance must use the following `author` block:

```json
"author": [
  { "@id": "https://axcentdance.com/#person1" },
  { "@id": "https://axcentdance.com/#person2" }
]
```

`#person1` = **Ale** (Co-Founder)
`#person2` = **Xidan** (Co-Founder)

These Person entities are fully declared in `about.html` with:
- `@type: Person`
- `name`, `jobTitle`, `image`
- `affiliation` → linked to `#organization`
- `sameAs` → `https://www.instagram.com/aleyxidan/`
- `description`

By using `@id` references, Google resolves the full Person entity from the site graph automatically. This is the most powerful E-E-A-T pattern available.

### ❌ Patterns Never to Use

```json
// WRONG — inline Organization as author
"author": { "@type": "Organization", "name": "AXcent Dance", "url": "..." }

// WRONG — inline Person without sameAs
"author": { "@type": "Person", "name": "Ale & Xidan", "url": "..." }

// WRONG — single @id pointing to organization
"author": { "@id": "https://axcentdance.com/#organization" }
```

### Publisher Pattern (keep as-is)

The `publisher` block should always point to the organization:

```json
"publisher": {
  "@type": "Organization",
  "name": "AXcent Dance",
  "logo": {
    "@type": "ImageObject",
    "url": "https://axcentdance.com/assets/images/logo.webp"
  }
}
```

> **Note:** `publisher` and `author` have different roles. `author` = the human creators (Person). `publisher` = the business entity (Organization). Never set publisher to a Person.

### Batch Upgrade Script (Author)

If you ever need to re-run the author upgrade across all blog posts:

```
/tmp/upgrade_author_to_person.py
```

Run from site root: `python3 /tmp/upgrade_author_to_person.py`
