# AXcentDance.github.io
AXcentDance Website

## Maintenance

To update `style.min.css`, `script.min.js`, and `llms-full.txt`, run the maintenance script:

```bash
python3 scripts/maintenance.py
```

## Breadcrumb Schema Maintenance

Use the breadcrumb maintenance script to validate JSON-LD breadcrumbs and apply narrow localized fixes without regenerating full page schema.

```bash
python3 scripts/maintain_breadcrumbs.py validate
python3 scripts/maintain_breadcrumbs.py fix --locale de --section blog-posts --dry-run
python3 scripts/maintain_breadcrumbs.py fix --locale de --section blog-posts --write
```

The script warns when the git working tree is dirty. It only refuses writes when a target file already has uncommitted changes, unless `--force` is passed. Reviewers should confirm that diffs only touch intended JSON-LD breadcrumb or `dateModified` fields, then run:

```bash
python3 scripts/breadcrumb_audit.py
git diff --check
```
