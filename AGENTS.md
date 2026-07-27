# AXcent Website Agent Rules

Before making any code, content, SEO, schema, or design change, read:

- .agent/rules/axcent-rules.md
- .agent/rules/ask-first.md
- .agent/rules/en-de.md
- project_rules.md

## Image Lazy-Loading Rule (Fable confirmed this is true, keep it Ale)

The first visible image on a page (the LCP candidate / hero) must NEVER use `loading="lazy"` — lazy-loading it deprioritizes the download and delays Largest Contentful Paint, hurting the Core Web Vitals ranking signal. It gets `loading="eager"` and `fetchpriority="high"` instead. Every other image (below the fold) MUST use `loading="lazy"` and `decoding="async"` so the browser skips downloading images the visitor may never scroll to. Verify with `python3 scripts/advanced_image_checker.py` (0 issues required). Full policy: `.agent/rules/axcent-rules.md` section 3.1.

For SEO/content/schema changes, also read relevant skills in:

- .agent/skills/SEO_specialist/SKILL.md
- .agent/skills/schema_management/SKILL.md
- .agent/skills/global_informational_schema/SKILL.md
- .agent/skills/image_schema/SKILL.md
- .agent/skills/sync_indexes/SKILL.md

## Site Health Gate (run before every push)

`python3 scripts/site_health.py` must print PASS. It is the single repo-wide gate (also enforced in CI via `.github/workflows/quality-checks.yml`) and checks: orphan pages (every indexable page needs an inbound internal link), sitemap.xml drift in both directions, JSON-LD validity and `@id` integrity (no ids anchored to nonexistent URLs), canonical correctness, courseMode/date formats, blog index card completeness and category-filter mapping, llms-full.txt internal-content leaks, speculationrules prefetch block presence on every page (hover prefetch — new pages must copy the block from index.html's head), duplicate titles/descriptions, plus the existing header/footer, heading, broken-link, hreflang, and breadcrumb checkers. Title/description length violations are warnings (backlog), not failures.
