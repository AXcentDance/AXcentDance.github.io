# AXcent Dance - Project Rules & Design Guidelines

> [!IMPORTANT]
> **Proactive Communication**: If you have ANY doubts about a technical requirement, SEO strategy, or content detail, you MUST ask the user for clarification before proceeding. Do not make assumptions on critical business logic.

## 1. Project Overview
**AXcent Dance** is a modern dance studio focusing on Bachata based in Zurich, Switzerland. The website should feel premium, elegant, connected, inviting, and energetic — never corporate and never like a generic template. The final color direction is still being decided (see Section 2.1); express the brand through typography, spacing, composition, photography, and motion rather than through any fixed palette.

**Studio Address**: Hermetschloostrasse 73, 8048, Zurich

## 2. Design System

### 2.1. Color Palette (Deliberately Undecided)
**STATUS**: The final brand palette is NOT fixed yet. The owner is still exploring color directions. The homepage currently prototypes one candidate ("Tropic Noir") via `tropic-noir.css`, scoped to the homepage only — see `System/homepage-revamp-strategy.md`. Do not treat it, or any hex values in the existing codebase, as final brand law.

Until a final palette is decided:

- Never hardcode colors inside components. All colors must flow through semantic CSS variables (`--bg-main`, `--bg-secondary`, `--bg-elevated`, `--text-main`, `--text-muted`, `--text-inverse`, accent tokens) so the palette can be swapped centrally at any time.
- Do not roll any experimental palette out beyond the homepage without explicit owner approval.
- Maintain WCAG AA contrast regardless of palette; CTA label text needs at least 4.5:1 against its button fill.
- When a task touches colors, ask the owner which direction applies or propose options — do not silently invent a new palette.

### 2.2. Typography
Use modern, elegant fonts available via Google Fonts. The typography should echo the logo's contrast between refined serif strength and fluid movement while remaining practical for a fast website.

- **Hero/Display Headings**: **'Cormorant Garamond'**, serif.
    - Weights: 600 (SemiBold), 700 (Bold).
    - Character: Elegant, expressive, and logo-adjacent. Use for hero statements and selected editorial headings only.
- **UI/Section Headings**: **'Outfit'**, sans-serif.
    - Weights: 600 (SemiBold), 700 (Bold).
    - Character: Geometric, friendly, and clean for scannable sections.
- **Body**: **'Inter'**, sans-serif.
    - Weights: 400 (Regular), 500 (Medium).
    - Character: Highly legible, neutral.
- **Script Personality**: Do not introduce decorative script fonts for navigation, body copy, or buttons. The logo already carries the script gesture; the website should translate that feeling through spacing, curves, motion lines, and composition.

### 2.3. UI Aesthetics
- **Surfaces**: Overlay surfaces (navbars, cards) use semantic tokens (`var(--glass-bg)`, `var(--glass-border)`, `var(--shadow-soft)`) — never hardcoded colors — so they follow whichever palette wins.
- **Shadows**: Soft, diffused shadows to create depth without harshness, defined as tokens.
- **Border Radius**: Generous curves to feel friendly.
    - Buttons: `30px` (Pill shape) or `12px` (Rounded rect).
    - Cards: `16px` to `24px`.
- **Accent Discipline**: Reserve the strongest accent for primary CTAs and key highlights; decorative accents stay thin and restrained (never large background fields).
- **Animations**: Smooth, organic, and Core Web Vitals safe.
    - `transition: opacity 0.3s ease, color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease`
    - Hover states may use color, opacity, border, underline, and shadow changes.
    - Do not use hover movement such as `transform: translate` or `scale` on layout elements.
- **GSAP & Three.js — Modern, Not "AI Slop"**: Use GSAP and Three.js as progressive enhancements for a modern, premium, crafted feel. Every effect must look intentional and brand-specific: purposeful scroll entrances, tasteful CTA/card micro-interactions, at most one ambient signature scene per viewport, and motion that references dance (rhythm, musicality, lead-and-follow). Avoid generic template effects — random floating shapes, particle explosions, neon glow spam, rotating conic borders, cursor-chasing blobs, parallax on everything. Preserve accessibility (`prefers-reduced-motion` static fallback, content visible without JS), semantic content, SEO clarity, and Core Web Vitals (lazy-init heavy scenes, pause offscreen, cap devicePixelRatio, never run WebGL over the hero video).

## 3. Coding Standards

### 3.1. HTML
- **Semantic Structure**: Use `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<article>` appropriately.
- **Accessibility**:
    - All images must have `alt` attributes.
    - Use ARIA labels where necessary.
    - Ensure logical heading hierarchy (`h1` -> `h2` -> `h3`).

### 3.2. CSS
- **Methodology**: Vanilla CSS with CSS Variables (Custom Properties) and BEM class naming.
- **Organization**:
    - Define variables in `:root`.
    - Use a Reset (e.g., box-sizing: border-box).
    - Group styles by component.
- **Responsiveness**: Mobile-first approach. Use media queries to adapt layout for tablets and desktops.
    - Breakpoints: `768px` (Tablet), `1024px` (Desktop).

### 3.3. JavaScript
- **Modern ES6+**: Use `const`/`let`, arrow functions, template literals.
- **Modularity**: Keep code organized.
- **Performance**: Defer script loading or use `type="module"`.

## 4. File Structure
```
/
├── index.html
├── style.css
├── script.js
├── project_rules.md
└── assets/
    ├── images/
    └── videos/
```

## 5. Technical & SEO Standards
**SYSTEM ROLE**: Senior Full-Stack Architect & Technical SEO Lead.
**CORE DIRECTIVE**: Produce code that is fully responsive and enforces strict metadata uniqueness.

### 5.1. Universal Responsiveness (Mobile + Desktop)
- **Breakpoint Strategy**: Use Flexbox/Grid to adapt from 320px to 1920px+.
- **Desktop Excellence**:
    - Implement hover states (cursor pointers, color shifts).
    - **STRICTLY FORBIDDEN**: No hovering animations that move elements (e.g., `transform: translate`, `scale`). This negatively impacts SEO/CLS.
    - Use screen real estate effectively (multi-column).
- **Mobile Excellence**:
    - Convert hover dependencies to click/touch.
    - Touch targets minimum 44px.
    - **Hamburger Menus**: Mandatory for screens <768px.
    - **Responsive Images**: Use `srcset` for mobile vs. desktop/retina.

### 5.2. Metadata & Vocabulary Uniqueness
- **"Anti-Duplication" Rule**: Strictly vary vocabulary even for similar topics.
- **Title Tags**:
    - Format: `[Unique Page Topic] | [Secondary Benefit] | [Brand]`
    - **Constraint**: Never repeat exact Title text.
- **Meta Descriptions**:
    - Must act as unique "ad copy".
    - Use synonyms and varied phrasing.
- **Alt Text**: Must describe specific image content relevant to page context.

### 5.3. Semantic HTML5 Architecture
- **Header & Footer**: Consistent components.
    - **Source of Truth**: The `index.html` file is the master reference for the Header and Footer. Any changes made to the Header or Footer must be first applied to `index.html` and then propagated to ALL other HTML files.
    - **Consistency**: They must be identical across all pages (except for necessary relative path adjustments in links and resources).
    - Header: Semantic `<nav>`, Logo (H1 on Home, Span/Div on subpages).
    - Footer: Copyright, Sitemap, Privacy, Terms, Socials, Address (Schema wrapped).
- **Headings**:
    - **H1**: Strictly ONE per page. Must be unique.
    - **H2-H6**: Logical hierarchy. Do not skip levels.
- **Tags**: No div soup. Use `<main>`, `<section>`, `<article>`, `<aside>`, `<header>`, `<footer>`.

### 5.4. Performance & Core Web Vitals
- **LCP**: Main desktop hero image must load instantly. **Do not lazy load the first image.**
- **CLS**: STRICTLY define `width` and `height` (or `aspect-ratio`) for all media to reserve space.
- **Code**: Minify CSS/JS concepts. Defer non-essential scripts.

### 5.5. Schema Markup (JSON-LD)
- **Identity**: Organization schema on Homepage.
- **Context**:
    - `FAQPage` for FAQ sections.
    - `BreadcrumbList` for hierarchy.
    - `Article` for blog posts (MUST include `"image"` field).
    - ensure `og:image` and `twitter:image` tags are present for all pages.
    - `Product` for items/services.
- **Schema Synchronization**: MANDATORY. Whenever any factual or transactional information (Dates, Prices, Artists, Locations, or event details) is changed in the page body, the corresponding JSON-LD Schema in the `<head>` MUST be updated immediately to ensure 100% parity between what the human sees and what the AI/Google reads. All timestamped dates (`datePublished`, `startDate`, `endDate`, etc.) MUST include the full time and UTC offset using the ISO 8601 format (e.g., `2025-12-07T12:00:00+01:00`). Exception: `dateModified` uses the date-only ISO 8601 format `YYYY-MM-DD` (schema.org permits `Date`), matching the site-wide convention enforced by `scripts/sync_blog_dates.py` and `.agent/rules/axcent-rules.md`.

## 6. SEO Guidelines (Yoast)

### Keyphrase Placement
- **Focus Keyphrase**: Must appear in SEO Title, Slug, Introduction (first paragraph), Subheadings (30-75%), Meta Description, and Image Alt Attributes.

### Keyphrase Density & Length
- **Frequency**: 0.5% - 3% density.
- **Length**: Keep keyphrase to 4 content words or fewer.
- **Uniqueness**: Do not reuse keyphrases across pages.

### Links
- **Outbound**: At least one link to an external domain.
- **Internal**: At least one link to another page on the site.

### Content & Technical
- **Text Length**: Min 300 words (Regular), Min 900 words (Cornerstone).
- **Title Width**: ~60 characters.
- **Meta Description**: 120-156 characters.
- **H1**: Only one H1 tag per page.

### Readability
- **Transition Words**: >30% of sentences.
- **Passive Voice**: <10%.
- **Sentence Length**: <25% of sentences >20 words.
- **Paragraph Length**: Max 150 words.
- **Flesch Reading Ease**: >60.

### Writing Style
- **No Abbreviations/Contractions**: Do not use contractions like "it's", "we'll", "won't", "can't". Always use the full form: "it is", "we will", "will not", "cannot".
