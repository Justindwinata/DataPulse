# DataPulse Roadmap

## DP-0001 - Project Bootstrap and Product Foundation

- Create repository structure.
- Add backend FastAPI foundation.
- Add frontend React foundation.
- Define initial data cleaning domain contracts.
- Add capabilities metadata endpoint.
- Document product scope and limitations.

## DP-0002 - File Intake and Validation

- Add file upload endpoint.
- Validate file extension, size, and basic content constraints.
- Store uploaded files temporarily for a cleaning session.
- Return clear validation errors.

## DP-0003 - CSV and Delimited Text Preview

- Detect CSV, TSV, and table-like text structure.
- Preview raw rows safely.
- Detect headers, delimiters, row widths, and empty rows.

## DP-0004 - Excel Sheet Discovery

- Detect workbook sheets for `.xlsx` and `.xls`.
- Support table-like sheet previews.
- Avoid claiming Excel formatting preservation.

## DP-0005 - Rule-Based Cleaning Engine

- Apply deterministic cleaning rules.
- Track before/after summaries.
- Keep transformations transparent and user-selected.

## DP-0006 - Export, Reports, and History

- Export cleaned CSV.
- Generate professional HTML cleaning reports.
- Add SQLite-backed cleaning history.
