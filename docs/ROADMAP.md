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
- Status: implemented for CSV-like files and selected Excel sheets.

## DP-0008 - HTML Cleaning Reports

- Generate professional HTML cleaning reports.
- Summarize validation, structure, quality, selected rules, rule effects, cleaned preview, export metadata, and limitations.
- Return standalone escaped HTML with no external scripts or CDNs.
- Add frontend Open HTML Cleaning Report workflow.
- Status: implemented.

## DP-0009 - Saved Cleaning History

- Add SQLite-backed cleaning history.
- Store metadata-first session summaries without original uploaded files.
- Let users save completed cleaning sessions.
- Let users list saved sessions, open detail, and delete local records.
- Status: implemented with local SQLite persistence.

## DP-0010 - Saved Session HTML Report Replay

- Generate saved HTML reports from stored session metadata.
- Avoid requiring original file re-upload.
- Clearly state that saved report replay is metadata-based.
- Add frontend Open Saved HTML Report action in History detail.
- Status: implemented.

## DP-0011 - Saved Rule Set Restore

- Reuse selected cleaning rules from a saved session.
- Require a fresh file upload before applying restored rules.
- Mark restored rules in the cleaning workflow.
- Allow users to edit or clear restored rules.
- Status: implemented.

## DP-0012 - Named Saved Workflow Templates

- Save reusable cleaning rule sets as named templates.
- Create templates from the current workflow or from saved session rules.
- Store template metadata locally in SQLite without original files or raw data.
- List, view, edit, apply, and delete workflow templates.
- Preselect template rules on a newly uploaded and profiled file.
- Status: implemented.

## DP-0013 - Product Stabilization and Demo Readiness

- Add QA checklist, demo script, portfolio notes, and synthetic demo files.
- Polish Workflow, History, and Templates navigation.
- Clarify workflow stages from upload through export/report/save.
- Improve empty, loading, and error states.
- Improve responsive layout and basic accessibility.
- Stabilize template ordering after edits.
- Status: implemented for local portfolio demo readiness.

## Later Ideas

- Template search, filtering, and import/export as portable JSON.
- Better type profiling for numeric and date columns.
- Safer large-file limits and streaming previews.
- PDF or richer report export options, if needed after the HTML report is stable.
- Screenshots and short demo video for GitHub/LinkedIn.
