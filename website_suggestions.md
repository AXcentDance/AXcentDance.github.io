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
## 2. File Organization & Cleanup
- **Root Directory Clutter**: There are several large media files in the root directory that should be moved to `assets/images` or `assets/video`:
    - `HeroVideoAleXidan.mp4`
    - `dominican_bootcamp.png`
    - `bachata_class_hero.png`
    - `milano-sensual-congress-logo.png`
    - `MilanoSensualCongress2026.jpg`
(Completed: Consolidate Styles)

## 3. SEO & Social Media
(Completed: Structured Data & Open Graph Check)

## 4. Performance
(Completed: Lazy Loading & Asset Versioning)

## 5. Functionality & Architecture
- **Form Migration to Supabase**: You are using `FormSubmit` (email) and Google Sheets, but also have Supabase initialized. Migrating contact/registration forms to Supabase would provide better data reliability and enable real-time admin dashboard updates.
- **Test Suite**: Add automated tests (Stick with Playwright or Cypress) to verify critical flows (Registration, Schedule loading).

## 6. Developer Experience (DX)
(Completed: Formatting & Git Ignore)

## 7. Security
(Completed: Content Security Policy)
