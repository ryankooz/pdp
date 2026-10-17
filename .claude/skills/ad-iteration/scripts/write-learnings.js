#!/usr/bin/env node
// Writes a confirmed learnings hypothesis back into a Growth Guide Google Sheet.
// Requires a service account JSON key at ~/.config/sheets-mcp/service-account.json
// (see the /ad-iteration SKILL.md "Growth Guide write-back setup" section for how to create one).
// The target sheet must be shared with that service account's email as Editor.
//
// Finds the row where the key column matches --batch, writes --text into the column
// named by --column (header match, case-insensitive). Appends a new row if no match
// and --append-if-missing is passed.
//
// Usage:
//   node write-learnings.js --sheet <SHEET_ID> --tab "2026 Ad Roadmap" \
//     --key-column "BATCH #" --batch 3 --column "LEARNINGS" --text "..." \
//     [--append-if-missing]

import { google } from "googleapis";
import { resolve } from "path";
import { existsSync } from "fs";

const CREDS_PATH = resolve(process.env.HOME, ".config/sheets-mcp/service-account.json");

if (!existsSync(CREDS_PATH)) {
  console.error(
    `No service account credentials found at ${CREDS_PATH}.\n` +
    `Follow the "Growth Guide write-back setup" steps in the ad-iteration SKILL.md to create one, ` +
    `then share your Growth Guide sheet with that service account's email as Editor.`
  );
  process.exit(1);
}

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return fallback;
  return process.argv[i + 1];
}

const sheetId = arg("sheet");
const tab = arg("tab");
const keyColumn = arg("key-column");
const batch = arg("batch");
const column = arg("column");
const text = arg("text");
const appendIfMissing = process.argv.includes("--append-if-missing");

if (!sheetId || !tab || !keyColumn || !batch || !column || !text) {
  console.error("Missing required args. See usage in file header.");
  process.exit(1);
}

const auth = new google.auth.GoogleAuth({
  keyFile: CREDS_PATH,
  scopes: ["https://www.googleapis.com/auth/spreadsheets"],
});

const sheets = google.sheets({ version: "v4", auth });

function colLetter(n) {
  let s = "";
  n += 1;
  while (n > 0) {
    const rem = (n - 1) % 26;
    s = String.fromCharCode(65 + rem) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

async function main() {
  const range = `'${tab}'!A1:ZZ`;
  const res = await sheets.spreadsheets.values.get({ spreadsheetId: sheetId, range });
  const rows = res.data.values || [];
  if (rows.length === 0) {
    console.error(`Tab "${tab}" is empty or not found.`);
    process.exit(1);
  }

  const header = rows[0].map(h => (h || "").toString().trim().toUpperCase());
  const keyIdx = header.indexOf(keyColumn.toUpperCase());
  const colIdx = header.indexOf(column.toUpperCase());

  if (keyIdx === -1) {
    console.error(`Key column "${keyColumn}" not found. Headers: ${header.join(", ")}`);
    process.exit(1);
  }
  if (colIdx === -1) {
    console.error(`Target column "${column}" not found. Headers: ${header.join(", ")}`);
    process.exit(1);
  }

  // Match on the numeric batch value only, anchored so "3" never matches "13" or "23".
  // A loose endsWith() check here previously caused batch 3 to match a row for batch 13
  // if that row appeared first in the sheet, silently writing into the wrong row.
  const needleDigits = batch.toString().trim().match(/\d+/);
  if (!needleDigits) {
    console.error(`--batch "${batch}" must contain a number.`);
    process.exit(1);
  }
  const needleNum = needleDigits[0];
  let rowIndex = -1;
  for (let i = 1; i < rows.length; i++) {
    const cell = (rows[i][keyIdx] || "").toString().trim();
    const cellDigits = cell.match(/(\d+)\s*$/);
    if (cellDigits && cellDigits[1] === needleNum) {
      rowIndex = i;
      break;
    }
  }

  if (rowIndex === -1) {
    if (!appendIfMissing) {
      console.error(`No row found where ${keyColumn} matches "${batch}". Pass --append-if-missing to add one.`);
      process.exit(1);
    }
    const newRow = new Array(header.length).fill("");
    newRow[keyIdx] = `BATCH#${needleNum}`;
    newRow[colIdx] = text;
    await sheets.spreadsheets.values.append({
      spreadsheetId: sheetId,
      range: `'${tab}'!A1`,
      valueInputOption: "USER_ENTERED",
      requestBody: { values: [newRow] },
    });
    console.log(`Appended new row for batch ${batch}.`);
    return;
  }

  const targetCell = `'${tab}'!${colLetter(colIdx)}${rowIndex + 1}`;
  await sheets.spreadsheets.values.update({
    spreadsheetId: sheetId,
    range: targetCell,
    valueInputOption: "USER_ENTERED",
    requestBody: { values: [[text]] },
  });
  console.log(`Updated ${targetCell} for batch ${batch}.`);
}

main().catch(err => {
  console.error("Sheet write failed:", err.message);
  process.exit(1);
});
