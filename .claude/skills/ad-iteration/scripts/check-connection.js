#!/usr/bin/env node
// Read-only check: confirms the local service account can authenticate and
// see the target sheet (metadata only, no cell reads or writes).
// Usage: node check-connection.js --sheet <SHEET_ID>

import { google } from "googleapis";
import { resolve } from "path";
import { existsSync } from "fs";

const CREDS_PATH = resolve(process.env.HOME, ".config/sheets-mcp/service-account.json");

function arg(name) {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? undefined : process.argv[i + 1];
}

const sheetId = arg("sheet");

if (!existsSync(CREDS_PATH)) {
  console.error(`MISSING_CREDENTIALS: no file at ${CREDS_PATH}`);
  process.exit(1);
}
if (!sheetId) {
  console.error("Usage: node check-connection.js --sheet <SHEET_ID>");
  process.exit(1);
}

const auth = new google.auth.GoogleAuth({
  keyFile: CREDS_PATH,
  scopes: ["https://www.googleapis.com/auth/spreadsheets.readonly"],
});

const sheets = google.sheets({ version: "v4", auth });

sheets.spreadsheets
  .get({ spreadsheetId: sheetId, fields: "properties.title,sheets.properties.title" })
  .then(res => {
    const tabs = res.data.sheets.map(s => s.properties.title).join(", ");
    console.log(`OK: connected to "${res.data.properties.title}". Tabs: ${tabs}`);
  })
  .catch(err => {
    console.error(`FAILED: ${err.message}`);
    console.error("Most likely cause: the sheet isn't shared with the service account's client_email yet, as Editor (or Viewer is enough for this read-only check).");
    process.exit(1);
  });
