# AXcent Dance — Homepage Revamp Strategy

*Produced 2026-07-02 by a four-role design review (visual designer, UX/UI engineer, GSAP animation specialist, creative technologist), cross-aligned into one system. Scope: `index.html` (homepage) only, desktop-first.*

> **Status (2026-07-02): Phase 1 implemented** via `tropic-noir.css`, a homepage-only stylesheet linked after `style.css` in `index.html`. All rules scoped to `body.home-page`; other pages untouched. Deferred from Phase 1: font-import pruning (Cormorant/Outfit ARE used by other pages, contrary to the original diagnosis), full duplicate-CSS consolidation, and the old-theme GSAP class-choice tween colors in `script.js` (superseded by Phase 3 anyway).
>
> **Status (2026-07-03): Style/motion pass implemented** (subset of Phases 3–4, homepage EN only, gated on the tropic-noir stylesheet):
> - **Motif system**: accent mark (´) + dancing underline on all `.section-title-modern` (tropic-noir.css §13; underline driven by `--title-underline-scale` from `enhanceTropicChoreography()` in script.js — three 0.18s steps + 0.24s expo tap).
> - **Texture**: static film grain (SVG feTurbulence, opacity 0.045, soft-light) + viewport vignette as `body.home-page::before/::after`, z 11990/11991 (above header 11000, below loader 20000).
> - **Lead & Follow choreography** for #about, #reviews, #trial-form header, FAQ (heading leads, content follows with 1-2-3-tap stagger); the `.reveal` slab is neutralized on the homepage in tropic-noir.css (content visible without JS / reduced motion). Beginner gateway and hero keep their existing entrances.
> - **Schedule "count-in"** replaces the old slab reveal inside `enhancePremiumTimetable()` (time column ticks first, cards slide laterally row by row); the legacy reveal remains as the fallback branch for the DE homepage.
> - **FAQ soft open**: animated height + rotating + icon; native toggle preserved for reduced motion / no JS.
> - Uses IntersectionObserver + GSAP core only (ScrollTrigger deferred until a scrubbed effect, e.g. gallery parallax, actually needs it).
> - Still open from the user's style list: nothing — remaining items below are the untouched backlog.
>
> **Status (2026-07-03, later): Reviews rail tempo easing implemented** (end of `enhanceTropicChoreography()` in script.js, tropic-gated): GSAP glide replaces the CSS `reviewsGlideLeft/Right` animation on the homepage; hover/focus eases `timeScale` to 0.15 over 0.6s instead of `animation-play-state: paused`; each review card counter-sways ±3px at offset phases; all loops pause offscreen via IntersectionObserver; pointer listeners gated to hover-capable devices; reduced motion keeps the existing static CSS fallback.
>
> **Status (2026-07-03, later): accent-mark signature REJECTED by owner and removed.** The slanted stroke (´) read as generic/AI-generated. Replacement title signature: an italic coral→amber **gradient keyword** in every section title (`<em class="title-accent">` on the emotive word — dancing, Bachata, Belong, connection, Stories, Questions) + the brass dancing underline. Assurance-line separators are now 1px brass hairlines. Do not reintroduce small stroke glyphs anywhere.
>
> **Status (2026-07-03, later): trial-form readability fix + hero H1 value proposition shipped.** The booking-process pills, form wrapper, and class-picker well were re-toned (old light-theme relics had white text on cream). The hero H1 is now "Learn Bachata in Zurich / No partner, no experience needed." (`.home-hero__headline`, roman + italic device); the brand display remains as a decorative `<p class="home-hero__title">` above it (one H1 on the page). The three assurance chips moved from the panel into `.home-hero__actions` under the primary CTA as solid pills over the video; both new elements joined the hero entrance timeline in `animateHomeHeroIntro()`. EN homepage only.
>
> **Status (2026-07-03, later): reviews-rail scroll-hijack bug fixed (global, style.css).** `.reviews-rail` had `overflow-x: auto` unconditionally, so a desktop mouse positioned over the reviews captured vertical wheel scroll and redirected it horizontally, stalling page scroll. Fixed by defaulting `.reviews-rail` to `overflow-x: hidden` and re-enabling `overflow-x: auto` + `scroll-snap-type: x proximity` only inside `@media (hover: none), (pointer: coarse)` (touch devices, where native swipe is still useful and there is no wheel to hijack). This is a global style.css fix (not tropic-gated) since `.reviews-rail` only exists on `index.html` / `de/index.html`, so both language versions are fixed. The GSAP tempo-glide (see above) drives the rail via `transform: translateX`, which does not depend on native scroll, so it is unaffected.
>
> **Status (2026-07-03, later): review-card scroll capture fixed + counter-sway removed (owner request).** The rail fix alone was insufficient — each `.review-card` was itself a scroll container (`overflow-y: auto`, fixed 14rem height), so the wheel was captured whenever the cursor sat on a card. Cards now default to `overflow: clip` with `.review-text` clamped to 5 lines (`-webkit-line-clamp`, ellipsis); the `@media (hover: none), (pointer: coarse)` block restores in-card scrolling and unclamped text for touch. **Important lesson: single-axis `overflow-x/y: hidden` silently promotes the OTHER axis from `visible` to `auto`, re-creating the scroll trap** — both `.reviews-rail` and `.review-card` needed `overflow: clip` (with `overflow: hidden` fallback), which removes the element from scroll-latching entirely. Verified: zero user-scrollable containers remain inside `#reviews` on desktop. Global style.css change (both homepages), cache-bumped to `style.css?v=8.4` on both. The ±3px vertical counter-sway on cards was removed from `enhanceTropicChoreography()` at the owner's request (`script.js?v=4.9`, EN only) — the tempo-eased glide and offscreen pause remain. Do not reintroduce per-card sway.
>
> **Status (2026-07-03, later): Phase 2 conversion fixes shipped (EN homepage; verified in preview).** Owner supplied the review count (40) and confirmed footer changes stay homepage-EN only. Details:
> - **Hero**: selector trimmed to the two real distinct videos (Bachata weekly + Dominican event) — Styling/Afro buttons cut because they replayed the same file at offsets; stage CTAs enlarged to 1rem/12.5rem min-width (tropic-noir.css §15).
> - **Schedule**: conversion offramp row under the grid ("…we will place you." + coral Book Free Trial pill, `.schedule-offramp`); brass "Start here" badge + static coral left border on Monday 18:30 Beginner 0 (`.tag-recommended`/`.class-card--recommended` — markup pre-existed from a parallel session, styles added in §15).
> - **Gateway→form preselection**: `data-preselect="beginner0"` wired on the Monday radio; `?class=beginner0#trial-form` verified end-to-end.
> - **About**: second H2 demoted to `h3.section-title-modern--sub` (2rem); founders strip added (`.founders-strip`: ale-xidan-about photo, "Founders, international Bachata artists, and official IDO Swiss Championship judges", link to /about).
> - **Reviews**: proof line is now a link — "5/5 from 40 Google reviews" → `maps?cid=15680757943659417558`; cards curated 14→8, beginner-transformation quotes lead both rails (Laura M, Federico M); brass initial-avatars (`.review-avatar`) with `.review-header` re-laid out (flex-start + badge margin-left auto).
> - **Trial form**: label "WhatsApp number or email" (`type="text"`, email-friendly placeholder); `novalidate` + bilingual INLINE validation replacing all three `alert()`s (shared script.js — errors render as `.form-error` with `role="alert"`, clear on input, first invalid field scrolled/focused; base colors in style.css for the DE dark theme, island colors #B3261E in tropic §15); "New? Start here" brass flag on the Beginner 0 option; "A real person confirms your spot on WhatsApp" microcopy.
> - **FAQ**: moved INSIDE `<main>`; inline styles → BEM classes (`.faq-item__summary/__icon/__body`, structural rules in tropic §15 — DE keeps its inline-styled copy untouched); new pricing question ("What happens after the free trial?" — 8-week blocks, 200/170 CHF, link to /registration) added to the page AND the FAQPage schema; post-FAQ re-ask CTA ("Still deciding? The first class is free." + coral pill). WebPage `dateModified` → 2026-07-03.
> - **Footer (EN only per owner)**: "Book Free Trial" first in Quick Links, visible WhatsApp line (+41 79 966 84 81 → wa.me), © 2026.
> - Cache bumps: `style.css?v=8.5`, `tropic-noir.css?v=1.6`, `script.js?v=5.0` (EN index.html only).
> - QA verified: one H1, no heading skips, 8 cards/8 avatars, FAQ in main, link targets exist, JS syntax clean, inline validation + preselection + FAQ soft-open exercised in the browser.
> - **Coordination note**: a parallel session was editing index.html simultaneously during this pass (it added the badges/preselect/offramp markup); one duplicate offramp was created and removed. Avoid concurrent sessions on this file.
>
> **Status (2026-07-03, later): hero selector restored to 4 real entries after owner correction.** The Phase 2 pass had trimmed the hero video selector to 2 buttons, misreading "Bachata Styling" (same file, `data-hero-start="10"`) as a meaningless duplicate — it is not: the page's own `VideoObject` schema defines distinct chaptered clips within `HeroVideo_mobile.mp4` (0-5s "Intense Connection", 5-11s "Sensual Techniques", 11-16s "Zurich Community Energy"), so seeking within one file is intentional, not filler. Restored. The owner also wants **Milano Sensual Congress** back as an event entry, but no dedicated video exists for it (the DE homepage's untouched original had it silently reusing `HeroVideo_mobile.mp4` at `start=0` — identical to the plain "Bachata" entry, a real duplicate). Instead of reintroducing that fake duplicate, added a small feature: `.home-hero__choice` buttons can now carry `data-hero-poster` instead of `data-hero-video`; the click handler (`script.js`, hero switcher block) pauses the video and crossfades in a new `<img data-hero-poster-frame>` sibling of the video (`assets/images/MilanoSensualCongress2026_1200w.webp`, CSS in style.css `.home-hero__poster-frame`/`.is-active`), instead of showing the same footage as another button. Picking a video choice again hides the poster and resumes/seeks normally. EN homepage only (DE still has its own 5-button block, untouched, using its old fake-duplicate approach — worth revisiting in a future DE-parity pass). Verified via programmatic click + computed style/class inspection; a `document.hidden` headless-tab artifact caused misleading paused/opacity readings mid-test, unrelated to the feature. Cache bumped to `style.css?v=8.6`, `script.js?v=5.1`.
>
> **Status (2026-07-03, later): beginner gateway compacted + recarded (owner request: "too big, too in your face").** Section scale stepped down in tropic-noir.css §16: title 5rem → clamp 1.9–2.8rem with the italic second line ("Start at the right level."), photo cards 23rem → ~14.5rem min-height with petrol shade replacing the old plum, cream mega-badges → small brass chips, "Try it free" → ink-on-coral pills (they previously had NO styles at all), and the start-bridge date line de-shouted (was 3.7rem coral uppercase wrapping 4 lines → one 1.35rem line under a small brass "Join any week" eyebrow). Cards are now **Bachata Beginner** (Monday 18:30 — fixed a data bug: the card said 19:30 while the schedule grid and its own form preselect said 18:30) and **Bachata Foundation** (Wednesday 19:30, `?class=foundation#trial-form` with new `data-preselect="foundation"` radio wiring, arrow → bachata-sensual-foundation, card image home/gallery_4). The Afro Beginner card was removed per owner. Copy reframed as a two-path chooser ("Start from zero" / "The next step") because Foundation (~1–1.5 years experience) is not a from-zero class and the old "start with other beginners" headline no longer covered both cards. EN only; DE gateway untouched. `tropic-noir.css?v=1.7`. Verification note: the preview browser served a stale prerendered copy after the edit (Speculation Rules); a cache-busting query param was needed to see changes — remember this when verifying.

> **Status (2026-07-04): Psychology conversion pass shipped (EN homepage; verified in preview).** Five changes from the 2026-07-04 front-page analysis:
> - **Hero "Your First Class" entry**: new first button in the Weekly Classes group of the selector ("Your First Class / What it really looks like") using the existing `data-hero-poster` mechanism with `assets/images/gallery/gallery_12_1200w.webp` (real students practicing). No beginner-class video exists yet — when a real 15-second Beginner 0 clip is filmed, swap `data-hero-poster` for `data-hero-video` on this button. Do NOT point it at existing pro footage (fake-duplicate rule).
> - **"Not sure — place me" escape hatch**: full-width `compact-option--unsure` radio below the class grid in trial-form Step 1 (`value="Not sure yet - Please recommend a class"`, `data-preselect="unsure"`); brass "Not sure?" chip + centered copy (tropic §22, with a ≤899px column-layout override because style.css forces `order: 3; margin-left: auto` on `.compact-status` there). The schedule offramp CTA now links `?class=unsure#trial-form` and preselects it (verified end-to-end).
> - **Price transparency + discounts**: `.trial-submit-pricing` line under the submit button (8-week blocks, 200 CHF ≈ 25 CHF/class, 15% off first sign-up, student discount, "No subscription, no pressure"); the 15% first-course discount was also added to the visible "What happens after the free trial?" FAQ AND its FAQPage schema text (kept in sync). "Student discount available" added as a fourth hero assurance chip.
> - **Response-time promise**: booking-process step 02 is now "We confirm by WhatsApp within a few hours"; Step 2 note now reads "…we always reply within a few hours."
> - **Mobile hero CTA regression FIXED**: style.css hides `.home-hero__actions` below 900px and expects a `.home-hero__panel-actions` block that the EN revamp had dropped (DE still has it) — so the EN mobile hero had NO CTAs and no assurance chips at all. Restored the panel-actions markup (Book Free Trial + Class Schedule) plus a `home-hero__assurance--panel` chip list after the H1; tropic §22 hides the panel list ≥900px (the stage overlay carries the chips there). Verified at 375/816/1280px.
> - Cache bump: `tropic-noir.css?v=3.0`. EN only — the DE homepage now lags on all of the above plus earlier passes; a DE-parity pass is overdue per the en-de rule.
>
> **Status (2026-07-04, later): Belonging/trust pass shipped (EN homepage; verified in preview).** Five copy/markup changes:
> - **Stat band belonging line**: first item label is now "dancers in our community — most walked in alone".
> - **Stat band trust slot — REJECTED by owner and reverted (2026-07-04, later)**: the "IDO" item had been replaced by `stat-band__item--faces` (44px circular Ale &amp; Xidan photo + "your teachers judge the IDO Swiss Championship"). The owner did not like the photo in the band; the item is back to the original "IDO / Swiss Championship judges" and the `.stat-band__faces` CSS was removed (cache bump `tropic-noir.css?v=3.2`). Do not reintroduce faces into the stat band; the founders strip in the About section remains the home for teacher faces.
> - **Gateway fear line**: subtitle now ends "Nervous? Everyone in Beginner 0 is a first-timer too."
> - **Form Step 2**: note now opens "Most people come alone."
> - **New FAQ (page + FAQPage schema, in sync)**: "Do I have to dance a specific role? Will there be enough partners?" inserted after the partner question — role choice regardless of gender, rotation, sign-up balance. FAQ count is now 9 in both places. OWNER TO CONFIRM the "keep the balance of leaders and followers in mind when confirming sign-ups" claim reflects real practice.
> - Cache bump: `tropic-noir.css?v=3.1`. EN only.
> - **Preview-harness note**: the preview tab can enter a broken zero-size / hidden state (window.innerWidth 0, screenshots time out, ALL `loading="lazy"` images defer because `document.hidden` is true). Restart the preview server AND resize the viewport to recover; verify lazy images via `fetch()` status or by forcing `img.loading='eager'`, not by `img.complete`.
>
> **Status (2026-07-04, later): mobile timetable readability bug FIXED (owner report: colors unreadable on the phone).** style.css's `@media (max-width: 899px)` block (~line 8100) paints `body.home-page .hidden-desktop .class-card` with the OLD light-theme cream gradient using `!important`, which beats the tropic dark card surface (`#10322B`, tropic line ~724, no `!important`) — so mobile showed tropic's cream/sage text on a cream card. Desktop was unaffected only because its style.css counterpart is not `!important`. Fixed in tropic (new max-899 block near §22): card background re-asserted `#10322B !important` (hover `#144036 !important`), brass hairline border, and `.mobile-time` moved from low-contrast bronze `var(--accent-bronze)` to brass `#E8B04B`. Verified at 375px (cards, times, badges, arrow chips all legible) and desktop 1280px unchanged. Cache bump `tropic-noir.css?v=3.3`. **Lesson: style.css still contains light-island mobile rules with `!important` that silently outrank tropic — check computed styles at mobile widths whenever a section looks right on desktop.** DE unaffected (does not load tropic, so its old light cards keep their original dark text).

> **Status (2026-07-05): mobile photo rail shipped (owner report: "Belong" photo section too long on the phone).** On ≤700px the four `.atelier-photo` figures stacked full width, running `#about` to 1,970px ≈ 2.4 viewports at 375×812. Now (tropic-noir, CSS-only, gated `@media (max-width: 700px) and (pointer: coarse)` per the reviews-rail wheel-capture lesson): `.atelier-fallback--story` becomes a swipeable flex rail (scroll-snap `x mandatory`, hidden scrollbar, tiles `flex: 0 0 82%` at 4/3 so the next photo peeks in as the affordance, `clip-path: none` on tiles). Also inside the same block: `.atelier-stage { min-height: 0 }` — the ≤1020px stage min-height clamp (tropic ~line 1817, 46rem = 736px) was sized for the stacked photos and otherwise leaves a ~300px void under the short rail (pre-existing override of style.css's mobile `min-height: 0`, masked until now). Result: photo block 982px → 211px, section 1,970px → 1,199px (1.48 viewports). Desktop collage and non-coarse narrow windows unchanged (rail is touch-only). Cache bump `tropic-noir.css?v=3.4`, EN only. **Preview note: the mobile preset does NOT emulate `pointer: coarse`** — the rail was verified by injecting the same rules without the pointer condition as a temporary page style; the shipped gated rules are byte-identical apart from that condition.

> **Status (2026-07-05, later): mobile photo rail REJECTED by owner ("didn't work") and replaced by an all-4 mosaic.** The rail's `(pointer: coarse)` gate meant it never activated in the preview panel / non-touch emulation, and the owner wanted all four photos visible at once anyway. New layout (same tropic block, now `@media (max-width: 700px)` with NO pointer condition — a static grid has no scroll-capture risk): `.atelier-fallback--story` is a 3-column magazine mosaic — the smiling-group hero photo spans full width at 16:9 (~343×193 at 375px), the other three sit under it as ~108px squares; captions hidden on mobile; `clip-path: none`. **Gotcha fixed during verification: the desktop collage assigns explicit `grid-column`/`grid-row` spans per photo (tropic ~lines 1787/1820) which leak into any new grid context — the mosaic must reset `grid-column/grid-row: auto` on tiles (hero: `1 / -1`).** Kept `.atelier-stage { min-height: 0 }`; added light compaction (header panel padding + title clamp 1.7–2.1rem, stay-copy padding). Result: photo block 310px, header + photos + gallery link = 560px (one phone screen), section 1,970px → 1,329px (1.64 viewports). Desktop collage unchanged (hero `grid-column: 1/6`, captions back), console clean. Cache bump `tropic-noir.css?v=3.5`, EN only. Do not reintroduce the swipe rail or pointer-gated layouts for this section.

> **Status (2026-07-05, later): timetable arrow chips fixed (owner report: arrows unreadable on desktop).** `body.home-page .class-card::after` in style.css (~line 8094, old light theme) draws the arrow chip as a cream circle `rgba(234,216,189,0.72)` with a BRASS `#E8B04B` SVG arrow — brass on cream is near-invisible, and the cream blob clashes with the tropic dark cards. Tropic override (scoped `.schedule-section .class-card::after`, next to the §19 tape-tick rules): chip goes dark brass-tinted `rgba(232,176,75,0.1)` with a `0.35` brass hairline (hover `0.2` / `0.6`); the brass arrow now reads at ~6.5:1. Applies to both the desktop grid and the mobile `.hidden-desktop` cards (same pseudo-element). Cache bump `tropic-noir.css?v=3.6`, EN only. Verified via computed pseudo-element styles; the preview screenshot pipeline was returning stale blank frames at the time (see preview-harness note above — `document.hidden` artifact persisted across a server restart this session).

> **Status (2026-07-05, later): beginner gateway photo cards REJECTED by owner and replaced by a self-selection fork.** The owner disliked the card presentation outright (second rejection of this section after "too big, too in your face"), so the format changed, not the scale: the gateway is now two typographic columns (`.starter-fork`, tropic §23) that each open with a first-person voice line — "I have never danced a step in my life." / "I already know my basic steps." — answered by the matching course (Bachata Beginner, Monday 18:30 / Bachata Foundation, Wednesday 19:30), split by a vertical brass hairline with an "or" chip (horizontal at ≤768px). Owner decisions from this pass: fork concept over question-chooser and journey-map alternatives; **fully typographic, no photos**; **September 7 applies to BOTH courses**; EN only. **Owner follow-up in the same pass: the first version was "too crammy" — copy was then cut hard.** The date now appears ONCE (subtitle: "Both begin the week of September 7 — come solo and pick the line that sounds like you."), the eyebrows are short ("Monday 18:30 · New cycle" / "Wednesday 19:30 · New course"), the promises are one line each ("Everyone in the room is a first-timer too. Join any week." / "Our new course — the gateway into Bachata Sensual."), the secondary link is "Details →", and §23 vertical margins were loosened. Keep this section SPARSE — do not add copy back. **Owner follow-up (same day): title alignment + course-name accuracy.** (1) The intro title/subtitle were still left-aligned — a leftover from style.css's shared `.guides-section .section-title-modern`/`.section-subtitle` rule (`text-align: left`), written when this section was a two-column layout with a side visual. The fork is single-column now, so tropic overrides `.guides-section--starter .guides-section__story`/`.section-title-modern`/`.section-subtitle` to `text-align: center` + `margin: auto`, matching the schedule/reviews/FAQ titles elsewhere on the page (verified: the existing dancing-underline motif already centers itself via `margin: auto` on its own pseudo-element, so it lined up automatically once the title box centered — no motif change needed). (2) Course names in the fork did not match the canonical names used in the schedule grid, trial-form radio values, and (for Foundation) the page's own Course schema: "Bachata Beginner" → **"Bachata Beginner 0"**, "Bachata Foundation" → **"Bachata Sensual Foundation"** (owner clarified the course teaches Bachata Sensual to people who already know regular Bachata's foundation/basics — confirmed against `bachata-sensual-foundation.html`'s H1 and Course schema, "Master Bachata Sensual foundations… for dancers with around 1-1.5 years of experience"). Foundation promise line reworded to "Now learn Bachata Sensual — body movement, isolation, and connection." to make that direction explicit. Cache bump `tropic-noir.css?v=3.9`. Verified centered at 1200px and 375px, links/headings/console clean.

> **Status (2026-07-05, later): typographic fork judged "too dry" by owner — upgraded to editorial duotone snapshots (fork concept retained).** Third styling iteration of the gateway, same self-selection narrative. Each `.starter-fork__path` now opens with a `figure.starter-fork__photo` (16:10 desktop / 16:9 mobile, 18px radius, brass hairline): **Beginner 0** uses `gallery/gallery_12_1200w.webp` (real students in class), **Sensual Foundation** uses `home/gallery_1_1200w.webp` (Ale &amp; Xidan in sensual partnerwork, portrait — `object-position: center 22%` keeps faces in the 16:10 crop). Photos wear the §17 About-collage **duotone filter recipe verbatim** (grayscale/sepia/hue-rotate 108deg petrol cast) + soft-light champagne/petrol scrim (`::before`), plus **floor-tape brass L-ticks on opposite corners** (`::after`, background-gradient technique — the §19 signature extended here); **colour blooms on `:hover`/`:focus-within` of the whole path** (filter transition, paint-only — same "colour is the reward" pattern as the collage). The voice line became a **caption strip overlapping the photo's bottom edge by ~22px** (`margin-top: -1.4rem`, solid `#08211C` backing, 2px brass left border) — the visitor "speaks over their own photo". Text now sits in a `.starter-fork__body` wrapper (`flex: 1`) so the CTA rows stay bottom-aligned across both columns. Images: lazy, explicit width/height, descriptive alts; both audit scripts clean. **Preview-harness note: the screenshot pipeline returned only blank/garbled frames this whole pass (across two server restarts, even with `document.hidden` false) — all verification was done via computed styles and geometry assertions (overlap px, aspect ratios, filter at rest vs focus-within, actions alignment); owner should eyeball the result in a real browser.** Also noted: a parallel session appended a contact-page tropic block (duplicate "§23" number) — untouched. Cache bump `tropic-noir.css?v=4.0`, EN only.
>
> **Phone compaction follow-up (owner: "too much written and too big pictures" on the phone; desktop approved).** CSS-only, inside §23's `@media (max-width: 768px)`: each path becomes a **thumbnail row** — the photo drops to a 6.5rem (104px) duotone square (12px radius, smaller 0.7rem tape ticks) in column 1 spanning two rows; the voice strip (1rem, no overlap in a row layout) and the body (course + eyebrow + CTAs) fill column 2 via `grid-template-areas: "photo voice" "photo body"` with `!important` (out-specifies style.css's max-767 "icon copy" `.guide-card` grid — verified the computed areas are ours). **`.starter-fork__promise` is `display: none` on phone** — the quote and the "New cycle"/"New course" eyebrow carry the message; the September 7 date stays in the subtitle. Result: path 176px (was ~420px), **section 1,150px → 688px** (fits one phone screen). Desktop verified unchanged (16:10 photo, 22px caption overlap, promise visible). **The screenshot pipeline recovered this pass** (fresh server, port 3000): both the 375px thumbnail rows and the desktop duotone composition were finally verified visually — the v4.0 design looks as intended (the course titles read slightly gold in JPEG screenshots; computed color is the intended champagne `#F4EFE6`). Console clean, link/heading audits pass. Cache bump `tropic-noir.css?v=4.1`, EN only. The `beginner-start-bridge` block was deleted (its WebGL rings scene bails safely — `if (!startBridge || !startCanvas) return`); title second line is now "Everyone starts somewhere." The path articles keep the `guide-card` class ONLY so `enhanceBeginnerGateway()` still gives them the rise entrance with zero script.js changes; their card skin is neutralised in §23 — including a `!important` re-assert inside `@media (max-width: 768px)` because style.css's max-767 block forces `.guide-card` into an "icon copy" grid with `!important` (the mobile-island lesson again; without it the voice line rendered as a squeezed side column). Dead tropic rules for `.beginner-course-card*`/`.beginner-start-bridge*` removed (style.css untouched — DE still uses them); `.starter-fork__trial` reuses the tier-2 CTA recipe verbatim and replaced the old trial link in the §21 focus-visible group. Verified: fork/divider at 1280px and 375px via computed styles, `?class=beginner0|foundation#trial-form` preselects end-to-end, both course links 200, console clean, ribbon canvas mounts, one H1 / no heading skips. **Preview-harness note: synthetic `preview_click` on the relative `?class=…#trial-form` links reports success but never navigates (also true for the pre-existing schedule offramp CTA) — verify preselection by navigating to the URL directly.** Cache bump `tropic-noir.css?v=3.8` (3.7 = fork, 3.8 = the de-cram trim), EN only (DE parity backlog grows).


> **Status (2026-07-09/10): SITE-WIDE ROLLOUT — waves 2–8 of System/site-revamp-plan.md shipped (EN).** Continuing the prior session's course exemplar (bachata-sensual-foundation) + registration work, this pass converted every remaining EN page except the five legacy course pages (owner: replicate only after the Foundation exemplar is approved):
> - **Blog unification (§10)**: `blog-post.css` rewritten as v2.0 — one Tropic Noir post template scoped to `body.post-page` covering BOTH legacy families (inline-style posts and v1.0 module posts). All 25 posts got `body="tropic post-page"`, tropic link, master footer (Maps iframe gone), a byline strip ("By Ale & Xidan · AXcent Dance · Meet your teachers"), a "Keep the rhythm going" recirculation band (trial + back-to-journal), `dateModified` → 2026-07-09, blob removal. 16 posts had stale headers missing the Corporate Events dropdown link — fixed. Legacy hover transforms (chapter-link slide, use-case-card lift) neutralised via scoped `transform: none !important`.
> - **schedule (§3)**: tropic timetable skin shared by widening 25 `body.home-page .schedule-*/.class-card/...` selectors to `:is(body.home-page, body.schedule-page)`; H1 de-shouted, fact chips, Start-here badge, offramp row (`/?class=unsure#trial-form` verified), journey timeline re-inked brass/coral with Teko 01–05 numerals (emoji removed), FAQ de-contracted with FAQPage schema synced 1:1, page's 270-line inline `<style>` deleted (ported), master footer.
> - **gallery (§4)**: natural order 1→15, 12-col magazine mosaic (tall/wide orientation classes), duotone-at-rest → colour on hover, always-visible brass caption eyebrows (old hover-reveal moved on hover — banned), first tile LCP eager+high, closing bridge (trial + Instagram).
> - **faq (§5)**: consolidated to 11 questions in three anchored groups (absorbed about.html's 3 + the homepage pricing question); accordion JS → native `<details>` with the shared `.sched-faq` skin; **payment answer corrected** (old copy claimed drop-ins/10-class-pass/monthly subscription — contradicted registration's 8-week blocks and the homepage "no subscription" line); FAQPage schema rebuilt to match visible 1:1 (verified in browser).
> - **about (§2)**: FAQ section + FAQPage schema node REMOVED (moved to faq.html); founders first; decorative "THE FOUNDERS" outline heading demoted to aria-hidden `<p>`; inner H2s → H3; globe moved below founders under "Taught around the world" with 3 stats (∞ Memories cut); globe scene re-inked in its own script (petrol land, sage borders, coral points); NEW visit-the-studio strip (2 duotone studio photos + map card); NEW closing trial bridge.
> - **services (§7)** with owner pricing decisions: private-lessons (quote-based — no public prices; emoji → brass numerals; NEW how-it-works count-in; Giulia P Google-review quote; inquiry band), wedding-dance (**CHF 800 package card** + Service/Offer schema node added; misnamed `.hero-video` div → real duotone `<img>`; NEW 3-question mini-FAQ; process H2s → H3), corporate-events (quote-based; bento re-inked, third card → inquiry band; header's rogue inline-styled dropdown link fixed), room-rental (**CHF 50 one-time business rate card + multi-week "get in touch" + active-student practice-discount brass callout**; champagne inquiry island — style.css forces `color: white !important` on `.form-input-modern`, so the island's ink text needs `!important`; specs emoji → brass ledger rows; purpose chips brass without hover movement).
> - **knowledge (§8)**: etiquette (15 rule cards, emoji → per-group Teko 01–05, hover slide removed, closing bridge), education (chapter numerals, brass anchor chips, callout class, cross-links → sensual guide/Foundation course/musicality post/etiquette), guide-bachata (palette graft ONLY: 13 hardcoded colours remapped petrol/brass/coral — including the white-on-coral CTA pill → ink; machine design untouched), guide-bachata-sensual (duotone hero interim `home/gallery_1`, Foundation funnel bridge with `?class=foundation` preselect), guide-social-dancing (chapter numerals, etiquette/events cross-band + trial CTA).
> - **utilities + legal (§11) + Milano (§9) + cart (§6)**: thank-you ×3 (brass check, tape-tick guide cards with numerals, WhatsApp reminder line), 404 ("This step is not in the choreography", Teko brass 404, three exits), privacy/terms/imprint (typography reskin; terms' photo hero + Unbounded font refs dropped; imprint's nonstandard logo markup normalised), Milano (H1 fixed "Upcoming Events" → "Milano Sensual Congress 2026", taped flyer poster eager LCP, Teko detail ledger), cart (petrol card, tier-1 Pay with Card, ALL Stripe/registration mechanics untouched).
> - **Coordinated bump**: every page linking tropic-noir.css now at `?v=5.0` (58 links incl. the 3 already-converted DE pages — cache-buster only, no DE design changes). `blog-post.css?v=2.0`.
> - **QA (all green)**: heading structure 0 issues, images 0 issues, broken links 0, JSON-LD parses on all EN pages, EN header/footer mismatches only on the five deliberately-deferred course pages (beginner-1/2, improver, inter-adv, lady-styling). Homepage regression-checked in preview (petrol canvas, fork, trial form, schedule cards, console clean); `?class=unsure#trial-form` preselection verified end-to-end by direct navigation.
> - **Open for owner**: the five course-page replications await exemplar approval + the Beginner 0/1 ladder explanation; faq payment-methods answer now says "Twint, cash, bank transfer, and secure card payment" — confirm card/Stripe is accepted for regular course blocks; wedding CHF 800 package inclusions ("song selection and editing support, filmed steps, final rehearsal") drafted from the private-lessons/wedding copy — confirm wording.

---

## 1. Executive diagnosis — why the page feels predictable

1. **The purple never earns brand recognition.** `--bg-main: #050208` / `--bg-secondary: #0f0816` are so close to black that the plum only surfaces as a muddy tint in the glass panels — it desaturates the warm accents without ever reading as a color.
2. **One gradient does everything, so it signifies nothing.** `var(--grad)` (#ff3b30→#ff6b1a) appears 19 times — logo, CTAs, badges, underlines, dividers. Its stops are ~25° apart in hue, so it reads as a flat red smear.
3. **Glassmorphism as default surface** — 57 `backdrop-filter` instances of white-hairline blur boxes, the most templated "dark modern site" pattern of the last five years.
4. **CTA language reads gamer/crypto, not premium** — neon glow box-shadow + rotating conic-gradient border on `.btn-hero-primary`.
5. **Zero motif, texture, or sectional rhythm** — all nine sections are centered italic Playfair on flat black; the section-title underline was even deleted (`.section-title-modern::after { content: none }`).
6. **Generic motion** — the monolithic `.reveal` slab-fade with six inconsistent easings across the codebase; also no reduced-motion override and content is invisible if JS fails.
7. **Conversion plumbing leaks** — H1 carries no value proposition, the mid-page has a ~2.5-viewport CTA gap, the 5/5 Google rating is unlinked and uncounted, no instructor faces, no pricing signal.

---

## 2. Color palette options

### Option A — "Ember Noir" (warm evolution, lowest risk)

| Token | Hex |
|---|---|
| bg-main | `#140B06` espresso black |
| bg-secondary | `#1E120A` |
| surface/card | `#26170D` (solid, no blur) |
| accent-primary | `#FF4D2E` → `#FFB25C` (flame → molten amber) |
| accent-secondary | `#E9C893` champagne gold |
| text-main / muted | `#F7F2EA` / `#B5A795` |
| heading | `#F3E6CF` |

Keeps the owner-approved fire, swaps the cold purple canvas for warm espresso. Candlelight-bar premium. CTA text must be ink `#1C0F08` (white on flame fails AA at body size).

### Option B — "Tropic Noir" ⭐ RECOMMENDED (bold, ownable)

| Token | Hex | Contrast on bg-main |
|---|---|---|
| bg-main | `#061A17` deep petrol green | — |
| bg-secondary | `#0C2A24` | — |
| surface/card | `#10322B` (solid, no blur) | — |
| accent-primary | `#FF5A3C` flame coral | 6.5:1 as text ✓ |
| accent-secondary | `#E8B04B` brass | 9:1 as text ✓ |
| text-main | `#F4EFE6` | ~16:1 ✓ |
| text-muted | `#9DB4AB` sage | ~8:1 ✓ |
| heading | `#F2E7CF` champagne | — |
| CTA ink (text on coral) | `#10231F` | 5.5:1 on coral ✓ |

Virtually no dance studio uses deep green — the niche is saturated with black/red, purple/pink, and neon. Petrol + coral + brass is luxury-hospitality language (Caribbean night, rum bar). The coral is a direct descendant of the current red-orange, giving continuity in the accents while replacing the failed canvas. Ownable: "the green-and-flame studio."

**Rule: never white-on-coral at body size (3.1:1 — fails). All coral CTA fills take ink text.**

### Option C — "Gallery Ivory" (boldest departure, highest cost)

| Token | Hex |
|---|---|
| bg-main / secondary | `#F6F0E4` / `#EFE6D4` warm ivory |
| surface | `#FFFDF7`, hairline `#E2D5BD` |
| accent-primary | `#C73A12` vermilion |
| accent-secondary | `#123C34` deep pine |
| text-main / muted | `#1D130B` / `#6D6154` |

Dark video hero stays, body flips to warm gallery-white. Highest distinctiveness, highest risk — largest rebuild of 12k lines of dark-assuming CSS.

### Tropic Noir usage map

| Section | Treatment |
|---|---|
| Header | Transparent → scrolled `rgba(6,26,23,.85)` + blur; logo "DANCE" in brass (kill `.text-gradient`); CTA pill = solid coral fill + ink text, hover `#FF7156` + 1px brass offset outline |
| Hero | Overlay retinted petrol; champagne headline with coral accent mark over the X; primary CTA coral/ink; secondary = transparent + brass hairline; assurance list `#F4EFE6` with brass tick bullets |
| Beginner gateway | bg-secondary + grain; cards `#10322B` with corner ticks; brass hairline chips; coral arrows |
| Schedule | bg-main; brass hairline column rules; hover = 3px coral left border + lift; times champagne (Teko); "Start here" badge = brass fill + ink text; "Full" badge sage-muted |
| About/values | bg-secondary; photos duotone (petrol shadows / champagne highlights); active toggle coral |
| Reviews | bg-main; stars brass (not red); names champagne; corner ticks |
| Trial form | **Conversion island: invert** — champagne panel `#F4ECD9`, ink text, coral/ink submit, 2px coral focus rings, errors `#B3261E`. The single light block on the page pulls the eye to conversion |
| FAQ | bg-secondary; open item brass left border; question hover coral |
| Footer | `#041310`; headings champagne; links muted → coral hover; brass icons |

---

## 3. Signature visual details (the ownable kit)

1. **The Accent Mark (´)** — a short 12°-slanted coral stroke above the X in AXcent, reused above every section title, as list bullets, and as nav active-state. Literal brand pun; trivial CSS.
2. **The Dancing Underline** — 2px **brass** rule under section titles that draws in on scroll in the bachata basic: `scaleX 0 → .33 → .66 → 1.04 → 1` (three 0.18s `power2.out` steps + 0.24s `expo.out` settle, ~0.78s, origin left, once at 70% entry), with **one coral dot** at the rule's end that ticks on the 1.04 overshoot (the "tap"). *Mark = identity, underline = rhythm. This is the merged motif — the 8-dot pulse concept was folded into it.*
3. **Floor-tape corner ticks** — replace full glass borders with corner-only L-marks (brass, coral on hover) referencing dance-floor tape. Kills the template glass-card look.
4. **Ink-on-coral editorial CTA** — no glow, no rotating border. Hover: label nudges 2px, brass 1px offset outline slides to 3px/3px (0.22s). Press: button translates 2px toward the outline ("stepping into the frame"), releases with `expo.out`.
5. **Film grain + vignette** — inline SVG `feTurbulence` data-URI, monochrome, **opacity 0.035, `mix-blend-mode: soft-light`** (overlay would desaturate the petrol); vignette fades to `#03100D`, never pure black. ~1.2KB, no JS.
6. **Branded duotone photography** — petrol shadows / champagne highlights across gallery and cards.

**Typography:** keep Playfair Display (headings) + Inter (body); **demote Teko to numerals only** (schedule times, stats). Delete unused imports (Cormorant Garamond, Outfit, Urbanist). One device: Playfair *italic* reserved for the second line of two-line titles.

---

## 4. GSAP motion plan

**Motion identity — "Lead & Follow":** one lead element moves first, siblings answer a half-beat later; small lateral travel (12–24px max) over big vertical drops; soft settles, no bounce; accents brief and rare. Max one ambient loop per viewport.

```js
const MOTION = {
  ease: 'power3.out',        // entrances
  easeSoft: 'sine.inOut',    // ambient
  easeAccent: 'expo.out',    // rare accents
  accent: 0.3, step: 0.6, phrase: 0.9,  // durations (s)
  beat: 0.07                 // stagger unit; +1 beat breath every 4th item
};
```

Add ScrollTrigger via CDN (~13KB gz) after the existing GSAP tag; delete the four redundant GSAP lazy-loaders in `script.js` (−2–3KB). Net ≤ ~16KB.

| # | Animation | Where | Trigger | Purpose | Priority |
|---|---|---|---|---|---|
| 1 | "First Step" hero entrance — brand letters settle laterally, video follows 1.015→1, CTAs stagger in | Hero | Load | States identity in first impression | Must |
| 2 | "Lead & Follow" section choreography — h2 leads, cards follow with 1-2-3-tap stagger; replaces `.reveal` slab | All sections | Scroll, once | Kills the template feel sitewide | Must |
| 3 | Dancing underline (see §3) | Section titles | Scroll, once | Signature rhythm motif | Must |
| 4 | Editorial CTA micro-interaction (see §3) + one entrance tap on primary CTA | CTAs | Hover/press | Tactile confidence at conversion points | Must |
| 5 | Reviews rail tempo easing — GSAP loop; hover eases `timeScale → 0.15` over 0.6s; ±3px sway per card | Reviews | Ambient/hover | DJ-easing-the-tempo feel, not video-pause | Must |
| 6 | Hero video dissolve — outgoing `autoAlpha→0` 0.18s; incoming from `autoAlpha 0, scale 1.015` 0.35s on `loadedmetadata`; shade constant | Hero selector | Click | Premium switch, no flash | Must |
| 7 | Hero→gateway scroll cue — 28px brass hairline, coral dot steps down in 3 pulses + pause; self-destructs on first scroll | Below hero panel | Ambient | Guides into the funnel | Nice |
| 8 | Schedule "count-in" — rows slide `x:-14→0`; time column ticks first like a metronome | Schedule | Scroll, once | Rehearsal count-in feel | Nice |
| 9 | Gallery counter-sway parallax — photos `yPercent ±3–4`, odd/even opposed, `scrub 0.6`, desktop ≥1024px only | About | Scroll scrub | Collage breathes; partners in opposition | Nice |
| 10 | FAQ soft open — `+` rotates 45°, height fromTo | FAQ | Click | Removes native snap | Nice |

**Form rule (UX-adjudicated):** no ambient/entrance motion on the trial form. Keep only action-response feedback: selection ring (replaces the repaint-heavy `boxShadow` tween — a net perf fix) and submit dip.

**Performance & a11y:** everything in `gsap.matchMedia('(prefers-reduced-motion: no-preference)')` — fixes the current gap where `.reveal` animates for RM users. Initial hidden states set from JS (`gsap.set`), never in the stylesheet — fixes invisible-content-without-JS and keeps CLS at 0. Transform/opacity only; `once: true` triggers self-destruct; only the gallery scrub + reviews ticker persist, paused offscreen.

---

## 5. Three.js / decoration plan

**Existing stack (important):** `script.js` already dynamically imports `three@0.160.0` (`loadThreeModule()`, ~line 518) and runs three WebGL micro-scenes (gateway ribbons/particles, start-bridge rings, trial-process canvas) with IO gating, RM bailout, DPR cap 1.5, low-power. **Reuse this loader; work inside `enhanceStartBridge`/guides code (~lines 500–900), not alongside it.** Gaps to fix: add a shared `visibilitychange` pause manager; consider consolidating contexts.

**Hero is a WebGL no-fly zone** — the video owns the GPU there. Never instantiate a renderer while the hero is in viewport; defer first Three import until hero video `canplay` AND gateway IO fires.

| Concept | Where | Tech | Spec (Tropic Noir) | Priority |
|---|---|---|---|---|
| **C2 Silk Ribbon** ⭐ signature | Beginner gateway canvas (replaces existing line-ribbons; mount + loader exist) | Three.js, 1 mesh / 1 draw call | Gradient along band: `#0C2A24` → `#FF5A3C` → **explicit warm stop `#F58042`** → `#E8B04B`; champagne `#F2E7CF` sheen at ~0.35 intensity, broad falloff (silk, not chrome); fold tint `#041310`; ambient glow ≤ `rgba(255,90,60,0.06)` | High |
| C1 Ember Glow | Hero panel/buttons | CSS div + `gsap.quickTo()` | `radial-gradient(circle 480px, rgba(255,90,60,0.07), rgba(232,176,75,0.03) 40%, transparent 70%)`, `mix-blend-mode: screen`; 0.8s ease follow; static centered on touch/RM | High |
| C3 Grain + vignette | Full page | CSS/SVG, no JS | See §3 item 5 | High |
| C5 Depth parallax | Gallery photos | GSAP ScrollTrigger | = GSAP idea #9 (shared; ScrollTrigger's 13KB owned by GSAP budget) | Med |
| C6 Bokeh dust | Behind reviews | Canvas 2D sprites | Coral `rgba(255,90,60,0.10)`, brass `rgba(232,176,75,0.08)`, champagne `rgba(242,231,207,0.05)`; composite `lighter`; cut first if trimming | Low |

**Silk Ribbon shader caveats:** set `premultipliedAlpha: true` and multiply rgb by alpha (avoids dark edge halos); add ±1/255 dither in fragment (coral/brass on dark petrol bands on 8-bit panels; grain overlay also masks it); no bloom postprocessing — sheen falloff only. Drop `antialias` on this scene.

**Budget:** three.module.js is already being fetched; net-new custom code ~12KB + GSAP's ~16KB ≈ **≤ 30KB gz added total**. Mobile: grain + static glow only (gate WebGL behind `min-width: 900px` + hardware checks).

---

## 6. Section-by-section improvements (UX × color × motion)

### Header (`.main-header`, :274)
- `.btn-header-cta`: ghost → **solid coral/ink** — the only solid coral in the header. *(High benefit, S effort)*
- Promote Beginner Guide out of the "More ▾" dropdown or rely on gateway links.
- Consider `body.home-page` context-aware "Our classes" → `#schedule` anchor to keep momentum toward the form.

### Hero (`#hero`, :322)
- **H1 rewrite (top conversion fix):** currently just the brand at 1.62rem vs 5rem H2s. New H1 = benefit + location ("Learn Bachata in Zurich — no partner, no experience needed"); brand stays in the logo.
- Move the three assurance chips ("Beginner friendly / No experience / No partner") directly under the primary CTA; enlarge "Book Free Trial" to clear desktop dominance.
- Hero panel secondary text: `#9DB4AB` at **0.95rem / 1.6 line-height** (was 0.82rem gray — below premium legibility).
- Fix the selector: 3 of 5 choices play the same file at different offsets; trim to real distinct clips or cut until assets exist. Apply motion #6 dissolve.

### Beginner gateway (`#new-to-dancing`, :406)
- Add "Try it free →" secondary CTA per card → `#trial-form` with class radio preselected (binding exists in script.js).
- Resolve the contradiction: "starts Week of Sept 7" vs FAQ "join anytime" → "Join any week — the next beginner cycle starts Sept 7."
- Align both cards to guide pages (Afro currently exits to a blog post). Silk Ribbon lives here.

### Schedule (`#schedule`, :465)
- **Add a conversion offramp row under the grid:** "Not sure which level fits? Book a free trial — we'll place you." → `#trial-form` (closes a ~2.5-viewport CTA gap).
- "Start here" badge (brass/ink) on Monday 18:30 Beginner 0 + 3px coral left border on that card.
- Keep the "Full" badge scarcity signal, sage-muted.

### About / gallery (`#about`, :631)
- Merge the two competing H2s into one argument (demote one to subhead).
- `.stay-link` "Book a free trial" → **primary button**, coral/ink with inverted hover (ink fill, coral text/border) so it reads intentional next to other CTAs.
- **Add a founders strip** — Ale & Xidan photo, one-line credential, link to /about. Reviews name them constantly; the page never shows them. Duotone treatment on photos.

### Reviews (`#reviews`, :724)
- Rating must be verifiable: "5/5 **from N Google reviews**", linked to the Google profile (CID already in the page head).
- Curate 14 cards → ~8; **lead with beginner-transformation quotes** (Laura M's "complete beginner… social dancing in weeks" is the page's best conversion asset, currently buried).
- Add initial-avatars; brass stars; motion #5 tempo easing; C6 bokeh behind (optional).

### Trial form (`#trial-form`, :1051)
- Core is strong (2 fields, 01→03 explainer, "No payment required today") — preserve.
- Label → "WhatsApp number (or email)" (script already accepts emails silently).
- Replace native `alert()` validation with inline field errors (`#B3261E` on the champagne panel).
- Highlight beginner options in the class picker ("New? Start here") + support preselection from gateway/schedule links.
- Sell the human touchpoint: "a real person confirms your spot on WhatsApp."
- Visual: the inverted champagne "conversion island" (§2 map).

### FAQ (:1259)
- **Add a pricing question** ("What happens after the free trial?" with range or link) — hidden pricing is a top abandonment driver in this vertical.
- Add a post-FAQ re-ask: "Still deciding? Book a free trial →".
- Housekeeping: move inline styles to classes, move the section inside `<main>`, make the `+` become "−" (motion #10).

### Footer (:1319)
- Add "Book Free Trial" as the first footer link; add visible phone/WhatsApp text near the address.
- Fix "© 2025" → 2026.

---

## 7. Priority implementation roadmap

| Phase | Work | Benefit | Effort |
|---|---|---|---|
| **1. Foundation** (do first) | Tropic Noir tokens in `:root`; retint overlays/glass→solid surfaces; ink-on-coral CTA system (kill glow + conic border); typography cleanup (drop unused fonts, Teko→numerals); consolidate duplicate CSS definitions | The identity shift itself; perf + maintainability | M |
| **2. Conversion fixes** | H1 rewrite + assurance chips at CTA; linked/quantified Google rating + curated reviews; schedule offramp row + "Start here" badge; gateway "Try it free" preselect links; `.stay-link` → button; form label/validation polish; pricing FAQ; footer fixes | Highest direct signup impact — mostly copy/markup, ship fast | S–M |
| **3. Motion system** | ScrollTrigger in; delete `.reveal` slab + 4 redundant loaders; Lead & Follow choreography; dancing underline + accent mark; CTA micro-interactions; hero entrance + dissolve; reviews tempo easing | Perceived-quality jump; fixes RM + no-JS defects | M |
| **4. Signature pieces** | Silk Ribbon shader (in existing canvas); Ember Glow; grain + vignette; founders strip w/ duotone; parallax; scroll cue; bokeh (optional) | Memorability — "that site with the silk ribbon" | M–L |

**Cross-cutting:** all colors via CSS variables (single-point palette control); AA minimums enforced (ink-on-coral everywhere, never white-on-coral body text); `prefers-reduced-motion` honored globally via `gsap.matchMedia`; mobile degrades to grain + static glow, no WebGL; CLS 0 (transform/opacity only, JS-set initial states); net JS/asset budget ≤ ~30KB gz.

---

## 8. Best direction — summary

**Go with Tropic Noir + "Lead & Follow" motion + the Silk Ribbon as flagship.** Deep petrol green (`#061A17`) replaces the muddy near-black purple and instantly differentiates AXcent from every black/red/purple dance site, while flame coral (`#FF5A3C`) keeps continuity with the fire you already chose — the palette says "Caribbean night, premium hospitality," which is exactly bachata in Zurich. The visual signature is a small, coherent kit: the coral accent mark, the brass dancing underline that literally steps the bachata basic, floor-tape corner ticks, film grain, and one champagne-lit silk ribbon in the beginner gateway. Motion is restrained and rhythmic (lateral settles, half-beat staggers, one tap accent), and every decorative choice doubles as a conversion device — the inverted champagne trial form is the brightest object on the page, the header CTA is the only solid coral in the nav, and the beginner path is preselected end-to-end. Phase 1+2 alone (tokens + conversion fixes) deliver most of the business value in days; phases 3–4 make it memorable.
