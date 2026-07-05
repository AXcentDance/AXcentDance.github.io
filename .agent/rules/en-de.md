---
trigger: always_on
---

Every time a change is made on the website — content, structure, SEO, forms, connectors, images, or anything else — the change must happen on both the EN version and the DE version in an equivalent way.

Verification: after any multi-page or structural change, run `python3 scripts/sync_audit.py` (every EN page has a DE counterpart) and `python3 scripts/en_de_parity_checker.py` (structural parity: headings, schema types, hreflang) from the repository root. Both must pass before the task is complete.