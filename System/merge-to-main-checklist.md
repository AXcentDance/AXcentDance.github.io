# Merge-to-main launch checklist

Things to do or verify on the day `revamp` merges into `main`. The scheduled
GitHub workflows only run from the default branch, so several systems switch
on at that moment.

## Right after the merge

1. **Supabase Monitor** (`.github/workflows/supabase-monitor.yml`)
   - Check the Actions tab: the first scheduled run should appear within
     ~20-30 minutes and end green.
   - Verify it created the repository Actions variable
     `SUPABASE_MONITOR_STATE` (repo Settings -> Secrets and variables ->
     Actions -> Variables). If the run fails on the variable step, the
     GITHUB_TOKEN permission for variables needs a fix — small change.
   - Optional: trigger it manually once (Actions -> Supabase Monitor ->
     Run workflow) instead of waiting.
2. **Keep-alive** (`supabase-keepalive.yml`) activates too. It is now
   redundant next to the 20-minute monitor — keep or delete, either is fine.
3. **Sitemap workflow** keeps running as before.

## Cleanup before real students arrive

4. Delete the test fixtures from the live database:
   - auth user `slamitza+portaltest@gmail.com`
   - its registration, absences, attendance and request rows
   - test rows in the Requests Google Sheet
5. Remove `http://localhost:3000/...` entries from the Supabase auth
   redirect allowlist (dev convenience, not needed in production).
6. Rotate anything test-exposed if desired (test account password was typed
   in plain text during development; Resend key rotation was still open).

## Still undecided

7. **Database backups** — no backup exists anywhere (free tier has none).
   Options: Pro plan, or a weekly encrypted pg_dump GitHub Action (needs DB
   password + passphrase as repo secrets). Decide before relying on the
   portal as the single source of truth.
8. Historical customers (pre-July-2026 purchases) are not in the database —
   they cannot create portal accounts until their emails are imported from
   the old Google Sheet (signup is purchase-gated).
