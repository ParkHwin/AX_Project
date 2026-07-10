import * as XLSX from "xlsx";
import { HEADERS } from "../constants.js";

const TYPE_KEYWORDS = [
  { type: "재고", keywords: ["재고", "입고"] },
  { type: "출하", keywords: ["출하"] },
  { type: "출고", keywords: ["출고"] },
];

function detectTypeFromName(filename) {
  for (const { type, keywords } of TYPE_KEYWORDS) {
    if (keywords.some((k) => filename.includes(k))) return type;
  }
  return null;
}

function detectTypeFromHeaderRow(headerRow) {
  const set = new Set(headerRow);
  let best = null;
  let bestScore = 0;
  for (const type of Object.keys(HEADERS)) {
    const score = HEADERS[type].filter((h) => set.has(h)).length;
    if (score > bestScore) {
      bestScore = score;
      best = type;
    }
  }
  return bestScore >= 3 ? best : null;
}

function normalizeCell(v) {
  if (v instanceof Date) {
    const pad = (n) => String(n).padStart(2, "0");
    return `${v.getFullYear()}-${pad(v.getMonth() + 1)}-${pad(v.getDate())}`;
  }
  if (v === undefined || v === null) return "";
  return String(v).trim();
}

// Parses one uploaded .xlsx/.xls file and returns { type, rows, headerRow }.
// `type` is one of "재고" / "출하" / "출고", detected from the filename first
// and falling back to matching the sheet's header row against known columns.
export async function parseExcelFile(file) {
  const buffer = await file.arrayBuffer();
  const workbook = XLSX.read(buffer, { type: "array", cellDates: true });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  const rows2d = XLSX.utils.sheet_to_json(sheet, {
    header: 1,
    defval: "",
    blankrows: false,
  });

  if (!rows2d.length) {
    return { type: null, rows: [], headerRow: [] };
  }

  const headerRow = rows2d[0].map((h) => String(h ?? "").trim());
  const type = detectTypeFromName(file.name) || detectTypeFromHeaderRow(headerRow);

  if (!type) {
    return { type: null, rows: [], headerRow };
  }

  const expectedHeaders = HEADERS[type];
  const rows = rows2d
    .slice(1)
    .filter((r) => r.some((c) => c !== "" && c !== undefined && c !== null))
    .map((r) => {
      const obj = {};
      headerRow.forEach((h, i) => {
        if (expectedHeaders.includes(h)) {
          obj[h] = normalizeCell(r[i]);
        }
      });
      expectedHeaders.forEach((h) => {
        if (!(h in obj)) obj[h] = "";
      });
      return obj;
    });

  return { type, rows, headerRow };
}

export function exportRowsToExcel(rows, headers, filename) {
  const orderedRows = rows.map((r) => {
    const obj = {};
    headers.forEach((h) => {
      obj[h] = r[h] ?? "";
    });
    return obj;
  });
  const worksheet = XLSX.utils.json_to_sheet(orderedRows, { header: headers });
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");
  XLSX.writeFile(workbook, filename);
}
