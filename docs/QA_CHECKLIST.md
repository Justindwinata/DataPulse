# DataPulse QA Checklist

Use this checklist before recording a portfolio demo or pushing a milestone.

## Backend Checks

- `make backend-test` passes.
- `GET /health` returns `healthy`.
- Upload validation accepts `.csv`, `.tsv`, `.txt`, `.xlsx`, and compatible `.xls`.
- Upload validation rejects unsupported, empty, and oversized files clearly.
- CSV/TSV/TXT structure detection returns delimiter, header, warnings, and raw preview.
- Excel workbook discovery returns sheets before selected sheet preview.
- Excel selected sheet preview is values-only and requires `sheet_name`.
- Data quality profiling returns issue summary, severity counts, quality score, and column profiles.
- Cleaning preview applies only selected deterministic rules.
- Cleaned CSV export returns UTF-8 CSV with a safe filename.
- Live HTML reports escape dynamic values and return `text/html; charset=utf-8`.
- Saved sessions initialize SQLite automatically and do not store original uploaded files.
- Saved report replay is metadata-based and does not reprocess old files.
- Workflow templates store rule sets and metadata only.

## Frontend Checks

- Navigation exposes Workflow, History, and Templates clearly.
- Upload workspace explains supported formats and max size.
- Empty states explain what the user should do next.
- Loading states are visible for validation, structure detection, quality analysis, cleaning preview, export, reports, session saving, history loading, and template operations.
- Error states explain likely causes and next actions.
- Rule cards show recommended, restored, or template context without implying automatic cleaning.
- Export panel states CSV-first behavior.
- HTML report panels do not imply PDF export or saved cloud history.
- History detail states original files are not stored.
- Templates section states fresh uploads are required.

## Manual Browser Checks

- Upload `demo/messy_sales.csv` and validate it.
- Detect structure and confirm comma delimiter.
- Analyze quality and confirm missing, duplicate, whitespace, and empty-column issues appear.
- Select cleaning rules and generate cleaned preview.
- Download cleaned CSV and confirm it opens as readable CSV.
- Open live HTML report.
- Save cleaning session.
- Load History, open detail, open saved HTML report, reuse rules.
- Create a template from selected rules.
- Load Templates, edit template metadata/rules, apply template, clear template state, and delete template.

## Responsive Checks

Check these widths with browser dev tools:

- 1280 px
- 1024 px
- 768 px
- 390 px
- 320 px

Expected result:

- No page-level horizontal overflow.
- Tables scroll inside their bordered containers.
- Cards stack cleanly on narrow screens.
- Buttons remain readable and tappable.
- The workflow, History, and Templates sections remain reachable.

## Known Limitations To Preserve

- DataPulse is local-only.
- Original uploaded files are not stored.
- Saved history and templates are local SQLite only.
- Excel formatting, formulas, merged cell behavior, charts, and pivot tables are not preserved.
- Export is CSV-first.
- No AI/LLM cleaning.
- No authentication, cloud sync, deployment, PDF export, or XLSX export.
