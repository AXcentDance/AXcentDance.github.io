# AXcent Website Agent Rules

Before making any code, content, SEO, schema, or design change, read:

- .agent/rules/axcent-rules.md
- .agent/rules/ask-first.md
- .agent/rules/en-de.md
- project_rules.md

## Image Lazy-Loading Rule (Fable confirmed this is true, keep it Ale)

The first visible image on a page (the LCP candidate / hero) must NEVER use `loading="lazy"` — lazy-loading it deprioritizes the download and delays Largest Contentful Paint, hurting the Core Web Vitals ranking signal. It gets `loading="eager"` and `fetchpriority="high"` instead. Every other image (below the fold) MUST use `loading="lazy"` and `decoding="async"` so the browser skips downloading images the visitor may never scroll to. Verify with `python3 scripts/advanced_image_checker.py` (0 issues required). Full policy: `.agent/rules/axcent-rules.md` section 3.1.

## Image `sizes` Truth Rule

Every `img` with a w-descriptor `srcset` must carry a `sizes` attribute that matches the image's real rendered width — `sizes` values are CSS-pixel layout claims, not file choices, and a stale claim silently makes browsers download the wrong srcset file (measured 2026-08-02: a lying flat slot cost the gallery page 639 KB and phone blog visitors ~1 MB per view). The source of truth is rendered layout, enforced by two gates: `scripts/site_health.py` statically requires every instance to match the manifest in `scripts/data/sizes_manifest.json`, and `python3 scripts/sizes_truth_checker.py` measures every responsive image in headless Chrome at 375/768/1440 and fails on any rendered-vs-slot mismatch that flips the fetched file at DPR 1 or 2. After ANY change to image markup or layout-affecting CSS, run the truth checker; once it passes, re-bless with `python3 scripts/sizes_truth_checker.py --bless` so site_health accepts the new state. Full-bleed background heroes use `sizes="100vw"`; never reintroduce flat `480px/800px/1200px` slots.

For SEO/content/schema changes, also read relevant skills in:

- .agent/skills/SEO_specialist/SKILL.md
- .agent/skills/schema_management/SKILL.md
- .agent/skills/global_informational_schema/SKILL.md
- .agent/skills/image_schema/SKILL.md
- .agent/skills/sync_indexes/SKILL.md

## Site Health Gate (run before every push)

`python3 scripts/site_health.py` must print PASS. It is the single repo-wide gate (also enforced in CI via `.github/workflows/quality-checks.yml`) and checks: orphan pages (every indexable page needs an inbound internal link), sitemap.xml drift in both directions, JSON-LD validity and `@id` integrity (no ids anchored to nonexistent URLs), canonical correctness, courseMode/date formats, blog index card completeness and category-filter mapping, llms-full.txt internal-content leaks, speculationrules prefetch block presence on every page (hover prefetch — new pages must copy the block from index.html's head), page baseline (every page needs exactly one Content-Security-Policy meta, and every page with a header needs the skip link + `id="main-content"` target — new pages must copy both from index.html), script loading (every classic `<script src>` must carry `defer`/`async`/`type="module"` — Supabase auth pages excepted — and no `video[data-hls]` may carry the `autoplay` attribute; use `data-autoplay="1"`, see the video policy), minified-twin freshness (`scripts/minify_assets.py --check`: pages ship `style.min.css`/`blog-post.min.css`/`script.min.js`, regenerated after every source edit — see the Minified Twins Rule below), critical-CSS freshness (`scripts/critical_css.py --check`: every page's inline `<style data-critical>` block must match the current CSS sources and page body — see the One Stylesheet + Critical CSS Rule below), duplicate titles/descriptions, responsive-image `sizes` integrity (srcset images need a `sizes` attribute matching the blessed manifest, and `imagesizes` preload hints must mirror their image — see the Image `sizes` Truth Rule below), plus the existing header/footer, heading, broken-link, hreflang, and breadcrumb checkers. Title/description length violations are warnings (backlog), not failures. CI additionally runs `python3 scripts/sizes_truth_checker.py`, the in-browser rendered-truth gate behind that manifest.

## Minified Twins Rule

The three first-party bundles (`style.css`, `blog-post.css`, `script.js`) are the EDITING SURFACE; pages reference their minified twins (`*.min.css` / `script.min.js`). After ANY edit to a source file: run `python3 scripts/minify_assets.py`, then bump that twin's `?v=` query in one coordinated pass across all pages. site_health fails on stale twins, so this cannot be forgotten silently. Never hand-edit a `.min.` file; never point a page at an unminified source. `script-blog.min.js` is a separate hand-frozen slim script for blog pages — not part of the pipeline, do not overwrite. Vendored libraries also ship minified (`assets/vendor/*.min.*`; pinned esbuild, `--legal-comments=eof`).

## One Stylesheet + Critical CSS Rule (2026-08-14)

The site ships EXACTLY ONE full stylesheet: `style.min.css` (blog pages add `blog-post.min.css`). `tropic-noir.css` was merged verbatim into the tail of `style.css` on 2026-08-14 and is retired — never recreate a second site-wide sheet; new component styles go into `style.css` (the `tropic-noir--*.css` files are palette-lab variants for palette-preview.html only). `palette-preview.html` is a CLONE of `index.html` plus four deltas (noindex, the `#palette-css` swap link + `palette-preview-enhancements.css`, the `palette-preview-page` body class, the `#palette-switcher` panel) — after ANY homepage change run `python3 scripts/rebuild_palette_preview.py`, otherwise the palettes get judged against a stale homepage. No page may carry a render-blocking stylesheet link. Instead every page's head carries, in this order:

1. `<style data-critical="HASH">…</style>` — GENERATED above-the-fold CSS. Never hand-edit; regenerate with the INCREMENTAL pipeline (2026-08-16, see System/flatten/README.md): `python3 scripts/critical_css.py export` first — it diffs against `System/flatten/critical_map.json` and usually reports "0 pages need probing" (declaration edits, deletions), in which case run `python3 scripts/critical_css.py apply` directly. Only when export lists pages does the browser step run: `upload_sink.py` + open `/System/flatten/critical.html`, `await runCritical()` (probes only the listed pages, auto-POSTs to the sink) → `apply`.
2. The full sheet loaded async: `<link rel="stylesheet" href="…style.min.css?v=X" media="print" onload="this.media='all'" data-async-css>`.
3. `<noscript><link rel="stylesheet" …></noscript>` fallback.

`scripts/critical_css.py --check` (run by site_health) fails any page whose critical block is missing or stale — the hash covers the CSS sources AND the page body, so editing either demands a regenerate. NEW PAGES: copy the three-line pattern from index.html's head, leave the `<style data-critical>` content empty or copied, then run the pipeline — the gate will insist until it is fresh. The page CSPs keep `style-src 'unsafe-inline'` and `script-src 'unsafe-inline'` partly FOR this pattern — do not tighten those away without replacing the async-load mechanism.

## Performance Standing Rules (2026-08-14 Lighthouse workstream — keep these true)

- Every classic script deferred; heavy decorative libraries (three.js) dynamic-import behind `window.load` via `whenWindowLoaded()` in script.js.
- Autoplaying hero videos: `data-autoplay="1"` + `preload="none"` + a real poster `<img class="…__posterframe">` under the video (the LCP element) — full pattern in `.agent/rules/video_upload_policy.md`.
- The LCP element and its ancestors are never animated from opacity 0; overlays dismiss on DOMContentLoaded, not window.load (axcent-rules §4.1).
- Font budget: exactly four families — Playfair Display (the one display serif, real italic), Outfit, Inter, Teko — self-hosted; adding any font file needs owner sign-off (axcent-rules §2.2).
- Meta pixel bootstraps at window.load (meta-pixel.js, owner-approved 2026-08-14).
- Accessible color tokens live in the design-token `:root` block in `style.css` (the flattened Tropic Noir section) (`--accent-gold-deep`, `--accent-coral-deep`, `--accent-coral-bright`, `--accent-coral-fill`): on light champagne panels use the -deep text variants; small coral text on petrol chips uses -bright; coral fills under white label text use -fill. Never reintroduce base coral/brass in those contexts — Lighthouse accessibility is at 100 site-wide and must stay there.
