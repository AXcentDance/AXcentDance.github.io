// AXcent Dance — unified forms webhook (registration + contact + bootcamp + rental).
// Paste into Apps Script (Extensions > Apps Script) of the "Registration"
// spreadsheet and deploy as a Web app (Execute as: Me, Access: Anyone).
// To update the live script: Deploy > Manage deployments > pencil >
// Version: New version > Deploy (the URL stays the same — never "New deployment").
// Posting pages: registration.html + de twin (registration rows), script.js
// (contact + bootcamp rows), room-rental.html + de twin (rental rows).
// Rows are routed to tabs by the form_type field; no form_type = registration.

const REG_SHEET = 'Registrations';
const CONTACT_SHEET = 'Contacts';
const BOOTCAMP_SHEET = 'Bootcamp';
const RENTAL_SHEET = 'Rentals';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const clip = (v, n) => String(v == null ? '' : v).slice(0, n);

    const getSheet = (name, headers) => {
      let sheet = ss.getSheetByName(name);
      if (!sheet) sheet = ss.insertSheet(name);
      if (sheet.getLastRow() === 0) {
        sheet.appendRow(headers);
        sheet.setFrozenRows(1);
      }
      return sheet;
    };

    if (data.form_type === 'contact') {
      getSheet(CONTACT_SHEET,
        ['Timestamp', 'Name', 'Email', 'Phone', 'Message']
      ).appendRow([
        new Date(),
        clip(data.name, 120),
        clip(data.email, 255),
        clip(data.phone, 40),
        clip(data.message, 5000)
      ]);
    } else if (data.form_type === 'bootcamp') {
      getSheet(BOOTCAMP_SHEET,
        ['Timestamp', 'First Name', 'Last Name', 'Email', 'Phone', 'Selected Class']
      ).appendRow([
        new Date(),
        clip(data.firstname, 120),
        clip(data.lastname, 120),
        clip(data.email, 255),
        clip(data.phone, 40),
        clip(data.selected_class, 120)
      ]);
    } else if (data.form_type === 'rental') {
      getSheet(RENTAL_SHEET,
        ['Timestamp', 'First Name', 'Last Name', 'Business', 'Email', 'Phone',
         'Purpose', 'Frequency', 'Timing', 'Message']
      ).appendRow([
        new Date(),
        clip(data.first_name, 120),
        clip(data.last_name, 120),
        clip(data.business_name, 120),
        clip(data.email, 255),
        clip(data.phone, 40),
        clip(data.rental_purpose, 60),
        clip(data.frequency, 40),
        clip(data.timing, 255),
        clip(data.message, 5000)
      ]);
    } else {
      getSheet(REG_SHEET,
        ['Timestamp', 'First Name', 'Last Name', 'Email', 'Phone',
         'Pass Type', 'Student', 'Pass Start', 'Pass End',
         'Dates Unavailable', 'Newsletter', 'Selected Classes']
      ).appendRow([
        new Date(),
        clip(data.first_name, 120),
        clip(data.last_name, 120),
        clip(data.email, 255),
        clip(data.phone, 40),
        clip(data.pass_type, 60),
        data.is_student ? 'Yes' : 'No',
        clip(data.pass_start_date, 40),
        clip(data.pass_end_date, 40),
        clip(data.dates_unavailable, 1000),
        clip(data.axcent_news, 10),
        clip(data.selected_classes, 1000)
      ]);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
