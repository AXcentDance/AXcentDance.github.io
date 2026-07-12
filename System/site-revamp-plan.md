# AXcent Dance — EN Site Revamp Plan (all remaining pages)

*Produced 2026-07-07. Continues `System/homepage-revamp-strategy.md` (Tropic Noir prototype). Scope: every EN page that does not yet carry the Tropic Noir treatment. DE is explicitly out of scope for this pass (the DE-parity backlog grows accordingly and is tracked at the end).*

**Already treated (reference implementations):** `index.html` (home-page), `contact.html` (contact-page), `events.html` (events-page), `dominican-bootcamp.html` (events-page bootcamp-page), `beginner-guide.html` (guide-page), `blog/index.html` (blog-page).

**Palette reminder:** Tropic Noir is still a prototype direction, not final brand law. Everything below flows through the token remap in `tropic-noir.css` §1, so the palette stays swappable in one place.

---

## 0. Rollout architecture (applies to every page below)

1. **`body.tropic` shared-chrome hook (implemented 2026-07-07).** All 115 shared-chrome selector lists in `tropic-noir.css` now end with `body.tropic`. A new page joins the theme by carrying `class="tropic <name>-page"` and linking `tropic-noir.css` after `style.css`. It inherits: token remap, petrol canvas, header/nav, footer, three-tier CTA system, serif titles + `title-accent` gradient keyword + dancing underline (CSS-complete without JS), film grain + vignette, `.reveal` neutralisation, focus rings. Page-specific design lives in a new scoped block (`body.<name>-page …`) appended to `tropic-noir.css`.
2. **Master footer propagation.** Every EN subpage still carries the old footer (map iframe, © 2025, no WhatsApp line) — 68 header/footer-checker mismatches against `index.html`. Each revamped page receives the master footer verbatim (WhatsApp line, "Book Free Trial" first quick link, light map card instead of the ~500KB Maps iframe, © 2026) with only link paths adjusted (`#trial-form` → `/#trial-form`; `../` prefixes under `blog/`). This is also a sitewide performance win: the Maps iframe disappears from every page.
3. **Legacy cleanup per page:** remove `.blob` background divs (index.html no longer has them), migrate load-bearing inline styles into the scoped tropic block, delete dead head `<style>` rules where safe.
4. **SEO safety:** titles, meta descriptions, canonicals, hreflang, H1 text stay unchanged unless explicitly flagged below. Any blog post touched gets its `dateModified` bumped (house rule).
5. **Motion:** this pass is CSS-first (underline motif renders complete without JS; hover is a colour event, never movement). One small generic addition to `script.js`: a Lead & Follow entrance for elements marked `data-tropic-reveal` on `body.tropic` pages (IO + GSAP, reduced-motion and no-JS safe, initial states set from JS only). No per-page WebGL.
6. **Media placeholders:** where a section wants a photo/video that does not exist yet, we ship the best on-brand existing asset plus an HTML comment `<!-- MEDIA PLACEHOLDER: … -->` at the element, and the want is listed in §14 (media wishlist). No fake duplicates, no stock, no external placeholder services.
7. **Cache discipline:** one coordinated bump at the end — `tropic-noir.css?v=5.0` on all pages that link it (including the 6 existing ones), `blog-post.css?v=2.0`, `script.js` bumped only if touched.

---

## 1. Course pages — the flagship template (exemplar: `bachata-sensual-foundation.html`)

**Owner instruction: build ONE course page as the concept; the other course pages (`bachata-beginner-1/2`, `bachata-sensual-improver`, `bachata-sensual-inter-adv`, `lady-styling`) reuse it with copy swaps.** Lady Styling belongs to this family (it shares today's course-hero template and Course schema).

**Concept — "The Course Dossier."** A course page today is three paragraphs and a sticky button. The redesign reads like the studio's own rehearsal sheet for the course: what the hour looks like, what the syllabus is, who it is for, where it leads. Body: `tropic course-page`.

Section order:

1. **Masthead (split editorial, guide-masthead grammar).** Left: eyebrow "Weekly course · Wednesdays 19:30", H1 (unchanged text), one-line dek, and a brass **call-sheet ledger**: Day & Time / Level (~1–1.5 years or Beginner 2) / Studio (Altstetten) / Language (English) / Block (8 weeks · 200 CHF, 170 student) / Entry (join any week). CTAs: tier-1 "Book a Free Trial" → `/?class=foundation#trial-form` (preselection already wired), tier-2 "Register for the course" → `registration`. Right: duotone taped figure — `assets/images/home/gallery_1_1200w.webp` (Ale & Xidan partnerwork). *MEDIA PLACEHOLDER: real Foundation-class photo.*
2. **Syllabus — "What you will learn."** The course "rotates through 10 Fundamental Techniques" — that rotation becomes the visual signature: an editorial grid of the four confirmed content areas (fundamental techniques, isolations, frame & connection, foundational partnerwork) with brass numerals, plus a rotation band: "Structured around 10 fundamental techniques — the cycle repeats, so you can join any week." *CONTENT PLACEHOLDER: owner to supply the 10 technique names to upgrade this into a full 01–10 syllabus ledger.*
3. **"One night in the room" — the class hour as a count-in timeline** (schedule count-in grammar, static): 19:30 arrival & warm-up → solo technique → partnerwork → rotation & social practice. NEW information; copy kept generic. *OWNER TO CONFIRM the actual class structure.*
4. **Level fork — "Is this your class?"** Two first-person voice lines (starter-fork grammar, no photos): "I know my Bachata basics — I want the sensual style." → you are in the right room / "I have never danced a step." → Bachata Beginner 0, Mondays 18:30. Plus the escape hatch: "Not sure? Book a free trial — we will place you." → `/?class=unsure#trial-form`.
5. **Teachers strip** (founders-strip recipe verbatim): ale-xidan-about photo, IDO Swiss Championship judges credential, link to `about`.
6. **Pathway band — "Where this course leads."** A one-line brass path: Beginner 2 → **Foundation (you are here)** → Improver (Wed 20:30) → Intermediate (Thu 19:30) → Inter/Adv (Thu 20:30), each a link. Internal-linking win; answers "what happens after 8 weeks".
7. **Conversion island (champagne).** Trial CTA (tier-1), register (submit-style), price transparency line (200 CHF / 8 weeks ≈ 25 CHF per class · 15% off your first sign-up · student discount · no subscription), "A real person confirms your spot on WhatsApp."
8. **Course FAQ (petrol skin, visible only — no new FAQPage schema per house rule):** join mid-cycle? / partner? / what to wear? / missed weeks (make-up rule from terms §5).
9. **Mobile sticky trial bar** (home recipe, generalised to course pages).

Fixes: the literal `</head>>` typo; Course schema gains `offers` (CHF 200, consistent with registration's ItemList) and `coursePrerequisites`; footer/master, blobs out. *MEDIA WISHLIST: 15–30s class clip per course (HLS per video policy) — the masthead figure is designed to swap into a taped video frame when footage exists.*

**Replication note:** beginner-1/2, improver, inter-adv, lady-styling copy this file and change: copy, call-sheet values, preselect key, pathway highlight, syllabus items, FAQ answers, schema. No new CSS.

---

## 2. `about.html` — "The people behind the studio"

Keep the interactive globe (distinctive, owner-built) but re-tone it; reorder the page so faces come first.

1. **Masthead:** H1 unchanged; sub-line "Passion, technique, and community." Slim editorial header, no big hero block.
2. **Founders first** (moved up): editorial split — duotone taped portrait (`ale-xidan-about`), bio copy trimmed into: who they are → "As international artists" → "Our philosophy" (H2 → H3 hierarchy fixed, inline text-stroke ornament removed). Credential line matches the homepage founders strip (IDO judges).
3. **"Taught around the world" — globe + stat band.** Stats (25+ cities / 12 countries / 400+ dancers) become a brass Teko stat band (homepage grammar); globe colors re-inked via its init script: petrol water, champagne land, coral arcs/points. The globe stays lazy-loaded.
4. **"Curated experiences"** — the two organizer cards become event acts (events-page grammar): Dominican Bootcamp + Milano Congress, taped thumbnails, tier-2 CTAs.
5. **NEW "Visit the studio" strip:** two studio photos (`studio/studio_room_view_1/2`) + the homepage location-strip recipe (address, Tram 2 / Bus 31, map card). Answers "where is it" on the page where people vet the business.
6. **Cut:** the 3-item FAQ (fragmented duplicate of faq.html — its unique questions move there, see §5) and its FAQPage schema node. **Add:** closing bridge — "Come meet us in person. The first class is free." → trial.

---

## 3. `schedule.html` — "The week at AXcent"

Most of the timetable skin arrives free (tropic rules target `.schedule-section`, which this page already uses). Beyond that:

1. **Masthead:** compact editorial hero; H1 styled out of all-caps via CSS (text unchanged); fact chips: English taught · Zurich Altstetten · join any week.
2. **Timetable parity with homepage:** add `class-card--recommended` + "Start here" badge on Monday 18:30 Beginner 0, and the **schedule-offramp row** ("Not sure which level fits? … we will place you." → `/?class=unsure#trial-form`). Keep the instructor-approval class-note (unique to this page).
3. **Journey timeline** ("Your Dance Journey", 5 stages): keep content — it is the best unique material on the page — restyled as a brass count-in rail (numerals 01–05, coral active dot, Leader/Follower split preserved, emoji removed). Fix the duplicated `.journey-section` CSS block.
4. **Private classes band** → quiet tier-2 CTA band.
5. **FAQ:** keep the 5 questions (2 are schedule-unique), petrol skin, schema stays in sync.
6. Cleanup: dead `.schedule-hero` CSS (targets a class the page no longer uses), blobs, inline styles.

---

## 4. `gallery.html` — "Nights at the studio"

1. **Masthead slim** (H1 "Gallery" + one line).
2. **Magazine mosaic** (blog-index grid grammar): varied tile spans on a 12-col grid instead of the uniform grid; photos wear the §17 duotone at rest and bloom to colour on hover/focus (colour is the reward); captions become small brass eyebrows on the tile. Remove the fake `cursor: pointer` (there is no lightbox; tiles stop pretending to be buttons). Restore natural order 1→15.
3. **NEW closing bridge:** "Come make the next photo." → trial CTA + Instagram link (the page currently has zero CTAs).
4. Fixes: first tile gets `fetchpriority="high"` (it is the LCP); blobs out.

---

## 5. `faq.html` — the single FAQ home

1. **Masthead slim** with anchor chips: Before your first class · Money & logistics · Community & events.
2. **Consolidation (content move):** absorb the unique questions from about.html ("Are classes in English?", "Are the teachers certified?", "What is Bachata Sensual?") and add the pricing question from the homepage ("What happens after the free trial?"). faq.html becomes the canonical FAQ home; schedule.html keeps only its schedule-specific items; about.html drops its FAQ entirely.
3. **Mechanics:** convert the bespoke `.accordion-item` + inline JS to the homepage `<details>` BEM pattern (native, no-JS safe, soft-open skin). FAQPage schema updated to match the final visible list 1:1.
4. **Closing re-ask:** "Still deciding? The first class is free." → trial.

---

## 6. `registration.html` + `cart.html` — "The studio desk"

**All mechanics are preserved untouched:** pricing toggle, activation-date generator, class/role validation, Stripe link map, Apps Script + FormSubmit dual send, cart hand-off. This is a reskin plus microcopy.

1. **Masthead compact** (H1 unchanged), fact chips: 8-week blocks · student −15% · no subscription.
2. **Pass prices:** the table keeps its DOM (JS depends on it) and wears a champagne **pricing island** — the one light block above the fold; brass rules, ink text, the Regular/Student toggle as tier-2 pills.
3. **Form:** trial-form island treatment (champagne panel, ink labels, coral focus rings, `#B3261E` errors); the class-selection grid gets the compact-option skin from the homepage picker; Leader/Follower radios become role pills.
4. **NEW "What happens next" count-in** above the submit: 01 Pay securely via Stripe → 02 We add you to the class WhatsApp group → 03 See you in class. (Matches thank-you.html's promise.)
5. **FAQ** petrol skin; footer/master; blobs out.
6. **cart.html:** one petrol card on the canvas — logo mark, "Complete Registration", reassurance line, coral/ink "Pay with Card", quiet link back to registration. Error state styled the same.
7. **Flags for owner (not changed silently):** registration submissions CC a personal Gmail (`slamitza@gmail.com`) in public markup; homepage promises "15% off your first sign-up" while the table only shows the student −15% — reconcile.

---

## 7. Services family — `private-lessons`, `wedding-dance`, `corporate-events`, `room-rental`

One shared `service-page` recipe (masthead with eyebrow + duotone taped figure, floor-tape benefit cards, count-in process, champagne inquiry island, petrol FAQ, closing bridge), then per page:

- **private-lessons:** benefits trio keeps its content (emoji icons → brass numerals). **Fill the empty testimonial slot** with a real quote from the curated Google-review set. NEW "How it works" count-in: 01 Tell us your goal → 02 We propose a plan → 03 Train 1-on-1. Inquiry island CTA → `contact`. *CONTENT PLACEHOLDER: private-lesson pricing — owner to decide whether to publish.* *MEDIA PLACEHOLDER: real 1-on-1 lesson photo (interim: `private_lesson_hero`).*
- **wedding-dance:** rename the misnomer `.hero-video` (static image); keep the strong 01/02/03 process (already count-in shaped; H2 → H3 fix); NEW mini-FAQ (visible only): how many lessons? / when should we start? / can it be our song? CTA "Book a consultation" → `contact`. *MEDIA WISHLIST: 20s rehearsal clip of a real couple.*
- **corporate-events:** bento grid → two editorial acts (Team building / Parties & entertainment) + venue band cross-linking room-rental; "Request a Quote" mailto styled as the island CTA. Delete the dead `.service-card`/`.cta-box` head CSS. *MEDIA PLACEHOLDER: workshop photo with visible group (interim: `corporate_party_natural`).*
- **room-rental:** the inquiry form (works today) gets the champagne island; specs become a brass call-sheet ledger (140 m² etc.); the 12 purpose chips stay as brass chips; move the two `<style>` blocks out of `<main>`. Studio photos duotone-taped. Flag: `_cc` personal Gmail (same as registration).

---

## 8. Knowledge family — `education`, `etiquette`, `guide-bachata-sensual`, `guide-social-dancing`, `guide-bachata`

- **guide-bachata:** the "bachata-machine" scrollytelling is a keeper (bespoke, owner-approved design). Work = palette graft only: join the chrome (`tropic` class), re-ink its purple/red accents to coral/brass, its cream after-machine block becomes the champagne island (near-identical value already). No structural change.
- **guide-bachata-sensual:** currently three paragraphs on the old course template. New concept **"The style, explained"**: masthead (slim, duotone figure — *MEDIA PLACEHOLDER: real sensual partnerwork close-up; interim `home/gallery_1`*), key-elements trio as floor-tape cards (Body waves / Isolations / Close connection), **"Is it too intimate?" reassurance panel** (the page's best objection-handling copy, elevated to its own band), founders credential strip, and the funnel bridge: "Ready to learn it? Bachata Sensual Foundation, Wednesdays 19:30" → course page + trial. This page is the top-of-funnel for the flagship course — it finally links to it properly.
- **guide-social-dancing:** concept **"Your first social night"**: the four Q&A blocks become count-in chapters (01 What it is → 02 Lead & follow → 03 No partner needed → 04 It is easier than you think), then an etiquette cross-band ("Know the floor rules" → etiquette) and trial CTA.
- **etiquette:** keep the 3-group / 15-card structure (good content); cards get the floor-tape skin with brass numerals per group (01–05); hero stays (`connection-101` photo, duotone); closing bridge → beginner-guide + trial. Fix the 3-way schema/og/hero image mismatch (align on the visible hero).
- **education:** the knowledge hub keeps its anchor nav, now as the sticky filter-shelf grammar (blog-index); style cards + instrument list + glossary get petrol card/ledger skins; instruments cross-link guide-bachata's machine sections. Fix Article schema image → the real hero (`bachata_education_book`).

---

## 9. `Milano-Sensual-Congress-2026.html` — events act grammar

Adopt `tropic events-page congress-page` (the events CSS already contains the act/poster recipes):

1. **H1 fix:** currently "Upcoming Events" (wrong page identity) → "Milano Sensual Congress 2026" (title/meta already say this).
2. **One act:** flyer in the taped poster frame (permanent brass tape), copy beside it; the 6 detail items become the call-sheet ledger (Location / Date Nov 20–22 / Price €125 / Masterclasses / Jack & Jill / Code **AleyXidan**).
3. **CTA:** "Buy your pass" external (lasalsadelbaile) tier-1, "All AXcent events" tier-2 → `events`.
4. **More-events card** → the events-page bridge band (Dominican Bootcamp thumbnail).

---

## 10. Blog posts — one unified skin for all 25 (`blog/*.html`)

Two template families exist today (A: per-post inline `<style>` + `script.min.js`; B: `blog-post.css?v=1.0` modules). Unification:

1. **`blog-post.css` is rewritten as the single Tropic Noir post template, v2.0**, every selector scoped under `body.post-page` (out-specifies the per-post inline `<style>` blocks without editing 25 sets of legacy CSS). Modules: editorial post masthead (category eyebrow · date, serif title with dancing underline left-anchored, duotone hero figure with tape ticks), reading column (champagne headings, `#F4EFE6` body on petrol, coral links with brass hover), quote/highlight/bento/collage/result-card/figure re-inked, chapters sidebar (roots) re-inked, `.cta-box` → tier-2 band, FAQ skin, **NEW byline strip** ("By Ale & Xidan · AXcent Dance · updated {date}" — matches the BlogPosting schema, EEAT), **NEW closing recirculation band** ("Keep reading" → blog index + trial CTA; static, no JS).
2. **Every post** gets `body class="tropic post-page"`, the `../tropic-noir.css?v=5.0` + `../blog-post.css?v=2.0` links, master footer, blobs out — applied by script across the 25 files, then hand-checked on one post of each family (`roots-of-bachata`, `hack-your-happiness`).
3. **House rule:** every touched post's `dateModified` → 2026-07-07.
4. `blog-posts/*` redirect stubs untouched. `blog/index.html` untouched except the coordinated tropic version bump.

---

## 11. Utility pages — chrome-only skin

- **thank-you / thank-you-contact / thank-you-trial:** shared centered petrol card, brass check mark, message unchanged; thank-you-trial keeps its 3 guide cards (tape skin, emoji → brass numerals); thank-you.html gains "Keep an eye on WhatsApp — that is where your group invite arrives." Dead head CSS pruned.
- **404:** brass Teko "404", champagne "Page not found", three exits (Home / Schedule / Blog), grain does the rest.
- **cart:** see §6.
- **imprint / privacy / terms:** `legal-content` typography re-inked (serif champagne H1/H2, coral links, sage meta); terms drops its old photo hero for the same slim legal masthead as the other two (the 'Unbounded' font it references was never loaded); emails become mailto links. No content changes.

---

## 12. Content moves & eliminations (summary)

- about.html FAQ (3 items) → merged into faq.html; FAQPage schema removed from about.
- Homepage pricing FAQ answer reused on faq.html; schedule.html keeps only schedule-specific questions.
- Dead CSS deleted where identified (private-lessons `.pricing-*`, corporate `.service-card`, thank-you guides CSS on pages without the grid, schedule `.schedule-hero`).
- Empty placeholder directories (`private-classes/`, `bachata-sensual-improver-zurich/`, `room-rental/`, `contact-…-altstetten/`) flagged for deletion (owner call — they are live URLs only as empty listings).
- The four legacy course pages + lady-styling stay on the old template until the owner approves the Foundation exemplar, then replicate.

## 13. New information added (summary)

Course call-sheet ledger + pathway ladder + class-hour timeline; about studio-visit strip; registration "what happens next"; private-lessons process + testimonial; wedding mini-FAQ; blog bylines + recirculation; gallery CTA; congress call-sheet. All persuasion claims verifiable (prices from the live table, make-up rules from terms, credentials from existing pages).

## 14. Media wishlist (owner)

| Want | Where | Interim asset |
|---|---|---|
| Foundation class action photo + 15–30s clip (HLS) | course masthead | `home/gallery_1` |
| Per-course clips (Beginner 0/2, Improver, Inter/Adv, Lady Styling) | course mastheads on replication | gallery set |
| 1-on-1 private lesson photo | private-lessons | `private_lesson_hero` |
| Couple rehearsal clip (~20s) | wedding-dance | `wedding_dance_hero` |
| Corporate workshop group photo | corporate-events | `corporate_party_natural` |
| Sensual partnerwork close-up (editorial) | guide-bachata-sensual | `home/gallery_1` |
| Designed OG cards (deferred, per OG strategy memo) | sitewide | JPG hero crops |

## 15. Implementation order

1. Course exemplar (`bachata-sensual-foundation`) — defines the subpage grammar. 2. Blog unification (25 posts, one CSS file). 3. schedule / about / faq / gallery. 4. registration + cart. 5. Services four. 6. Knowledge five. 7. Milano congress. 8. Utilities. 9. QA suite (5-step + header/footer + en-de parity report), coordinated cache bump, strategy-doc status entry.

## 16. DE parity backlog created by this pass

Every page above now diverges from its DE counterpart in skin (and about/faq diverge in FAQ placement). DE remains on the old theme by owner instruction. A future DE pass replicates: body classes + tropic link + footer + per-page markup, translating only copy (`scripts/en_de_parity_checker.py` will enumerate).
