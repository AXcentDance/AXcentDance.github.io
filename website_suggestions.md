# Website Improvement Suggestions

Based on a review of the current project structure and content, here is a prioritized list of missing items and suggested improvements.

## 1. Essential Missing Pages
(Completed)

## 2. File Organization & Cleanup
- **Root Directory Clutter**: There are several large media files in the root directory that should be moved to `assets/images` or `assets/video`:
    - `HeroVideoAleXidan.mp4`
    - `dominican_bootcamp.png`
    - `bachata_class_hero.png`
    - `milano-sensual-congress-logo.png`
    - `MilanoSensualCongress2026.jpg`
- **Consolidate Styles**: Consider automated build steps to merge `style.css` and `style.min.css` so you only edit one source file (SASS/PostCSS).

## 3. SEO & Social Media
- **Structured Data Optimization**: You have `application/ld+json` for `DanceSchool` in `index.html`. Consider adding `Event` schema for your specific workshops or classes on `events.html`.
- **Open Graph Image Verification**: Ensure `assets/images/hero.webp` (referenced in your meta tags) exists and is optimized for link previews.

## 4. Performance
- **Image Formats**: Ensure *all* images are served as WebP or AVIF.
- **Lazy Loading**: Verify that off-screen images have `loading="lazy"` attributes.
- **Resource Caching**: Optimize browser caching strategies where possible.

## 5. Functionality & Architecture
- **Form Migration to Supabase**: You are using `FormSubmit` (email) and Google Sheets, but also have Supabase initialized. Migrating contact/registration forms to Supabase would provide better data reliability and enable real-time admin dashboard updates.
- **Test Suite**: Add automated tests (Stick with Playwright or Cypress) to verify critical flows (Registration, Schedule loading).

## 6. Developer Experience (DX)
- **Formatting & Linting**: Add `.prettierrc` and `.eslintrc` to ensure consistent code style.
- **Git Ignore**: Ensure large media files are managed properly.

## 7. Security
- **Content Security Policy (CSP)**: Add a CSP `<meta>` tag to prevent XSS attacks.
