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
