# Owner Requests → Google Sheet (setup guide)

The portal records every freeze / room booking / private class request in
Supabase (`requests` table, shown in `_admin.html`). This guide adds the
Google Sheet mirror: every request also lands as a row in your own
spreadsheet, via a Google Apps Script web app (same mechanism as the
registration form).

## One-time setup (about 5 minutes, in your Google account)

1. Go to https://sheets.google.com and create a **new blank spreadsheet**.
   Name it e.g. `AXcent Requests`.
2. In the sheet menu: **Extensions → Apps Script**.
3. Delete whatever is in the editor and paste the contents of
   `System/requests-sheet-appsscript.js` (in this repo).
4. Click **Deploy → New deployment**.
   - Click the gear icon next to "Select type" and choose **Web app**.
   - Description: `AXcent requests webhook`
   - Execute as: **Me**
   - Who has access: **Anyone** (required — the browser posts anonymously;
     the URL is unguessable and the script only appends rows).
5. Click **Deploy**, authorize with your Google account when prompted.
6. Copy the **Web app URL** (it looks like
   `https://script.google.com/macros/s/AKfycb.../exec`).
7. Paste that URL into the `REQUESTS_SHEET_URL` constant in BOTH
   `portal.html` and `de/portal.html` (currently an empty string), or hand
   it to Claude to wire in.

The sheet gets a `Requests` tab with a header row on the first submission:
Timestamp | Type | Name | Email | From | Until | Details.

## Notes

- Until the URL is set, the portal simply skips the Sheets mirror — the
  Supabase inbox and the notification emails keep working.
- If you later edit the script, use **Deploy → Manage deployments → Edit →
  New version**; the URL stays the same.
- The mirror is fire-and-forget from the browser (`no-cors`), so a Sheets
  outage can never break a customer request.
