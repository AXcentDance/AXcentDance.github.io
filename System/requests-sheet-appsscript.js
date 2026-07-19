// AXcent Dance — portal requests webhook.
// Paste into Apps Script (Extensions > Apps Script) of the requests
// spreadsheet and deploy as a Web app (Execute as: Me, Access: Anyone).
// See System/requests-sheet-setup.md for the full walkthrough.

const SHEET_NAME = 'Requests';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) sheet = ss.insertSheet(SHEET_NAME);

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['Timestamp', 'Type', 'Name', 'Email', 'From', 'Until', 'Details']);
      sheet.setFrozenRows(1);
    }

    const clip = (v, n) => String(v == null ? '' : v).slice(0, n);

    sheet.appendRow([
      new Date(),
      clip(data.type, 40),
      clip(data.name, 120),
      clip(data.email, 255),
      clip(data.date_from, 20),
      clip(data.date_until, 20),
      clip(data.details, 1000)
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
