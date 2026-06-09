# $gsc-report

Run this workflow when the user asks for `$gsc-report`, a GSC report, Search Console opportunities, or an actionable SEO report based on AXcent topic authority.

## Command

```bash
python3 scripts/gsc_topic_action.py
```

## Output

- `System/GSC_Topic_Action_Report.md`
- Uses private GSC OAuth files in `private/`
- Uses AXcent topic map files in `System/topic_map/`

## Rules

- Treat the output as private SEO intelligence.
- Do not paste OAuth secrets or raw token values.
- Do not edit website pages from this action unless the user separately asks for implementation.
- If any content change is later made, follow the EN/DE parity, schema, sitemap, and LLM context rules.
