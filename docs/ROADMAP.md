# DataPulse Roadmap

DataPulse will grow through small contracts so each stage remains reviewable, testable, and portfolio-friendly.

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
- Avoid permanent uploaded file storage.
- Return clear validation errors.
- Add frontend upload UI with validation feedback.
- Status: implemented.

## DP-0003 - CSV and Delimited Text Preview

- Detect CSV, TSV, and table-like text structure.
- Preview raw rows safely.
- Detect headers, delimiters, row widths, and empty rows.
- Return structured warnings and raw preview metadata.
- Status: implemented for CSV, TSV, and TXT.

## DP-0004 - Excel Sheet Discovery

- Detect workbook sheets for `.xlsx` and `.xls`.
- Support table-like sheet previews.
- Avoid claiming Excel formatting preservation.
- Add frontend sheet selector and selected sheet preview.
- Status: implemented for table-like Excel sheets.

## DP-0005 - Data Quality Issue Detection

- Detect common data quality issues from bounded samples.
- Return issue severity counts and a transparent heuristic quality score.
- Return column-level profiles with inferred types and missing-value metrics.
- Suggest future cleaning rules without applying them.
- Add frontend issue summary and column profile UI.
- Status: implemented for CSV, TSV, TXT, and selected Excel sheets.

## DP-0006 - Rule-Based Cleaning Engine

- Apply deterministic cleaning rules.
- Track before/after summaries.
- Keep transformations transparent and user-selected.
- Add cleaned preview.
- Status: implemented as sample-based cleaning preview.

## DP-0007 - Cleaned CSV Export

- Export cleaned CSV from selected deterministic rules.
- Keep export CSV-first.
- Avoid claiming Excel formatting preservation.

## DP-0008 - Reports and History

- Generate professional HTML cleaning reports.
- Add SQLite-backed cleaning history.

## Later Ideas

- Better type profiling for numeric and date columns.
- Safer large-file limits and streaming previews.
- More detailed cleaning report sections.
- Accessibility and keyboard workflow polish.
