# Tropic → style.css flattening workstream

Owner decision 2026-07-28: the Tropic Noir DESIGN is final; only palette values
remain open ("I will only change the color, not the style itself"). This
workstream merges tropic-noir.css into style.css component by component, ending
with one stylesheet and one `:root` token block that repaints the whole site.
See axcent-rules.md §2.1.

## Method (established by the buttons/CTA pilot, 2026-07-28)

1. **Match-set from the browser, declarations from the source.** Chrome's CSSOM
   is authoritative for WHICH rules match an element (`:is()`, media queries,
   complex selectors) but it DESTROYS authored declarations in one common
   pattern: a `background: var(--x)` shorthand followed by longhand overrides
   in the same rule serializes as empty-string longhands — `cssText`,
   `style.cssText`, and `getPropertyValue('background')` all return nothing.
   Tropic §4 uses exactly this pattern. Therefore: `harness.html`'s
   `matchSets()` exports the ordered matching-rule identities per element and
   state; the authored declarations are then joined from the byte-faithful
   Python parse (the CSS-purge analyzer's parser in the scratchpad
   css_purge/analyze.py — parser + specificity + context machinery reusable),
   and the cascade replay happens in Python.
2. **Specificity:** `:is()` takes its most-specific argument (all args in this
   codebase are `body.X` = 0,1,1). A naive class-count over the selector string
   OVERCOUNTS `:is()` lists — always normalize `:is(...)` to one `body._x`
   before counting.
3. **Scope dropping is proven safe for the button family:** every page
   containing any pilot button class carries at least one of the six scope
   classes (home-page/contact-page/events-page/blog-page/guide-page/tropic);
   the only 4 unscoped pages (portal/auth utilities) contain none of them.
   Re-run this proof per component family before dropping its `:is()` scope.
4. **Placement:** merged rules go in a new section at the END of style.css
   (preserves cascade position vs. everything earlier in style.css). Rules
   later in tropic-noir.css than the deleted block (e.g. hero-specific §5
   refinements at ~363-402, cta-premium at ~2422) remain later in the cascade
   and keep winning — leave them for their own component pass.
5. **Verification:** (a) fingerprint rig (iframe hash of geometry+styles,
   11 pages x 2 viewports — capture a FRESH baseline immediately before
   comparing; countdown pages drift within ~2h); (b) per-variant effective-
   declaration equality before/after via matchSets+replay; (c) hover/focus
   probes on the key CTAs; (d) site_health.py PASS.

## Pilot scope map (buttons/CTA family)

Five interacting layers:
- style.css base: .btn-header-cta 921, .btn-hero-primary 1453,
  .btn-hero-secondary 1476, .btn-submit 2373, .cta-outline/.cta-filled 4154+
  (line numbers as of v10.3)
- style.css legacy home-scoped block: 5427-5687 (cream-era header/hero CTA
  styling + conic border kills + luxury-glow vars)
- tropic-noir.css §4 CTA SYSTEM: lines ~198-332 (tier1/tier2/submit/secondary
  recipes + conic kill + sheen) — the block being flattened
- tropic-noir.css later refinements: hero-specific ~363-402, cta-premium
  ~2416-2430 (stay in place this pass)
- responsive variants in both files (style 955, 4188, 5427; mobile menu 1175)

Pilot status:
- Instrument built and hardened (two real CSSOM traps discovered and designed
  around); scope-droppability proven.
- STEP 1 DONE + VERIFIED 2026-07-28: tropic §4 relocated VERBATIM to the end
  of style.css (selectors untouched → specificity and matching identical, only
  cascade position moved). Proof: fresh pre/post fingerprints 22/22 identical,
  CTA computed-style probes identical at 1280px and 375px, site_health PASS.
  tropic-noir.css no longer contains the CTA system.
- STEP 2 (next): consolidation of the three now co-located layers in
  style.css (base rules ~921/1453/2373/4154, legacy home-scoped block
  ~5427-5687, relocated block at end). Requires extending the purge analyzer's
  pass-3b eligibility to expand `:is()` scope lists (it currently rejects any
  selector containing '(' — that is why it finds zero opportunities here).
  The hero classes (.btn-hero-primary/-secondary) may be whitelisted from the
  JS-poison guard: script.js:139-140 only querySelector-reads them.

Serve locally and open /System/flatten/harness.html; `extract()` (advisory,
replay-in-browser) and `matchSets()` (authoritative) run in the console.
