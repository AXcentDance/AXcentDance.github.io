# AXcent Dance - Project Rules & Design Guidelines

## 1. Project Overview
**AXcent Dance** is a modern dance studio focusing on Bachata based in Zurich, Switzerland. The website should reflect a "warm and connected" aesthetic, and a focus on inviting, premium feeling, focusing on human-connection.

**Studio Address**: Hermetschloostrasse 73, 8048, Zurich

## 2. Design System

### 2.1. Color Palette
The palette is "Warm Modern". It combines soft, inviting backgrounds with vibrant, energetic accents.

- **Primary Background**: `#FDFBF7` (Warm Off-White) - Used for main page backgrounds to create a welcoming atmosphere.
- **Secondary Background**: `#F2EFE9` (Warm Light Grey) - Used for sections or cards.
- **Primary Text**: `#2D2D2D` (Soft Charcoal) - High contrast but softer than pure black.
- **Secondary Text**: `#5C5C5C` (Warm Grey) - For subtitles and supporting text.
- **Brand Accent**: `#E05D44` (Terracotta/Coral) - energetic, warm, and modern. Used for primary buttons and key highlights.
- **Secondary Accent**: `#F4A261` (Soft Orange) - Used for gradients or subtle highlights.
- **Success/Info**: `#2A9D8F` (Teal) - For positive states, complements the warm tones.

### 2.2. Typography
Use modern, clean sans-serif fonts available via Google Fonts.

- **Headings**: **'Outfit'**, sans-serif.
    - Weights: 600 (SemiBold), 700 (Bold).
    - Character: Geometric but friendly.
- **Body**: **'Inter'**, sans-serif.
    - Weights: 400 (Regular), 500 (Medium).
    - Character: Highly legible, neutral.

### 2.3. UI Aesthetics
- **Glassmorphism**: Use subtle glass effects for overlays (navbars, cards).
    - Background: `rgba(255, 255, 255, 0.7)`
    - Blur: `backdrop-filter: blur(12px)`
    - Border: `1px solid rgba(255, 255, 255, 0.3)`
- **Shadows**: Soft, diffused shadows to create depth without harshness.
    - Example: `box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05)`
- **Border Radius**: Generous curves to feel friendly.
    - Buttons: `30px` (Pill shape) or `12px` (Rounded rect).
    - Cards: `16px` to `24px`.
- **Animations**: Smooth, organic transitions.
    - `transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)`
    - Micro-interactions on hover (slight lift, scale, or color shift).

## 3. Coding Standards

### 3.1. HTML
- **Semantic Structure**: Use `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<article>` appropriately.
- **Accessibility**:
    - All images must have `alt` attributes.
    - Use ARIA labels where necessary.
    - Ensure logical heading hierarchy (`h1` -> `h2` -> `h3`).

### 3.2. CSS
- **Methodology**: Vanilla CSS with CSS Variables (Custom Properties).
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
    - `Article` for blog posts.
    - `Product` for items/services.

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
