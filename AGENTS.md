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

`python3 scripts/site_health.py` must print PASS. It is the single repo-wide gate (also enforced in CI via `.github/workflows/quality-checks.yml`) and checks: orphan pages (every indexable page needs an inbound internal link), sitemap.xml drift in both directions, JSON-LD validity and `@id` integrity (no ids anchored to nonexistent URLs), canonical correctness, courseMode/date formats, blog index card completeness and category-filter mapping, llms-full.txt internal-content leaks, speculationrules prefetch block presence on every page (hover prefetch — new pages must copy the block from index.html's head), page baseline (every page needs exactly one Content-Security-Policy meta, and every page with a header needs the skip link + `id="main-content"` target — new pages must copy both from index.html), duplicate titles/descriptions, responsive-image `sizes` integrity (srcset images need a `sizes` attribute matching the blessed manifest, and `imagesizes` preload hints must mirror their image — see the Image `sizes` Truth Rule below), plus the existing header/footer, heading, broken-link, hreflang, and breadcrumb checkers. Title/description length violations are warnings (backlog), not failures. CI additionally runs `python3 scripts/sizes_truth_checker.py`, the in-browser rendered-truth gate behind that manifest.
