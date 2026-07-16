# DataPulse

DataPulse is a deterministic messy CSV and Excel cleaner studio. It helps users prepare table-like files for analysis through transparent validation, profiling, rule-based cleaning, preview, CSV-first export, and cleaning reports.

DataPulse is not an AI cleaning tool and does not claim perfect automatic cleaning. The product direction is deliberately rule-based: users should be able to see what was detected, choose which transformations to apply, and review what changed.

## Portfolio Demo Snapshot

DataPulse is now prepared for local portfolio demos. It includes:

- File validation for CSV, TSV, TXT, XLSX, and compatible XLS files
- CSV/TSV/TXT delimiter, header, structure, and raw preview detection
- Excel workbook sheet discovery and selected sheet preview
- Deterministic data quality profiling and heuristic quality score
- Rule-based cleaning preview with transparent rule effects
- Cleaned CSV download
- Standalone HTML cleaning reports
- Local SQLite saved cleaning sessions
- Saved-session HTML report replay
- Saved rule restore and named workflow templates
- Stitch-inspired SaaS platform UI across Home, Workspace, History, and Templates
- Synthetic demo files in `demo/`
- Demo script, QA checklist, and portfolio notes in `docs/`

## Screenshots

Screenshots are not committed yet. Recommended captures for GitHub/LinkedIn after starting the local app:

- First viewport with product shell, workflow CTA, and local-only scope panel
- Main workflow with upload validation and active stage cards
- Structure preview table and data quality issue summary
- Cleaning rule selection with selected-rule context and cleaned preview
- CSV export, HTML report, and save-session panels
- History detail with saved report replay
- Templates library and apply workflow

## Current Scope

DP-0001 established the product and engineering foundation:

- FastAPI backend package with service metadata and `GET /health`
- `GET /cleaning/capabilities` metadata endpoint
- Pydantic domain contracts for the future cleaning workflow
- React, TypeScript, Vite frontend foundation
- Vitest and Pytest tests from the beginning
- Root Makefile for repeatable local checks
- Product requirements, architecture notes, roadmap, decision log, and changelog

DP-0002 adds the first real file intake milestone:

- `POST /files/validate-upload` multipart upload validation endpoint
- Supported upload extensions: `.csv`, `.tsv`, `.txt`, `.xlsx`, and `.xls`
- 10 MB maximum upload size
- Empty file rejection
- Unsupported extension rejection
- Unsafe filename sanitization in response metadata
- Frontend upload validation workspace
- Accepted, rejected, loading, empty, and backend error UI states

Uploaded files are read only for validation metadata and are not stored permanently.

DP-0003 adds CSV-like structure detection and raw preview:

- `POST /files/detect-structure` multipart endpoint
- CSV, TSV, and TXT table-like structure detection
- Deterministic delimiter detection for comma, semicolon, tab, and pipe
- Simple header candidate detection
- Generated column names when no header is detected
- Bounded raw preview with up to 20 preview rows
- Structure warnings for inconsistent row widths, empty rows, duplicate headers, missing headers, leading metadata rows, and very small samples
- Honest Excel limitation response for `.xlsx` and `.xls`

Structure detection reads only a bounded sample for CSV-like files and does not store files permanently.

DP-0004 adds Excel sheet discovery and raw sheet preview:

- `.xlsx` workbook support through `openpyxl`
- `.xls` workbook support through `xlrd` where the uploaded workbook is compatible
- Workbook sheet discovery with sheet names, count, default sheet, and sheet metadata
- Selected sheet preview through optional `sheet_name` form field
- Header detection and generated column names for table-like sheets
- Bounded Excel preview with up to 20 preview rows
- Excel warnings for empty sheets, empty rows, empty columns, duplicate headers, missing headers, selected sheet not found, and sample limits
- Frontend sheet selector and selected sheet raw preview

Excel previews are values-only. Formatting, formulas as formulas, merged cell behavior, charts, pivot tables, macros, and workbook styling are not preserved.

DP-0005 adds deterministic data quality profiling:

- `POST /files/detect-quality` multipart endpoint
- CSV, TSV, TXT, XLSX, and compatible XLS quality profiling
- Optional `sheet_name` form field for Excel selected-sheet profiling
- Clear sheet-selection-required response when Excel quality analysis is requested without a sheet
- Sample-based issue detection for missing values, empty rows, empty columns, duplicate rows, duplicate headers, missing headers, messy headers, inconsistent row widths, whitespace, mixed type patterns, numeric-looking text, date-looking text, and high-missing columns
- Column-level profiles with missing counts, missing percentages, inferred type, unique count, sample values, and issue codes
- Transparent heuristic quality score based on issue severity
- Frontend quality summary cards, issue cards, and column profile table

DataPulse reports suggested future cleaning rules, but it does not apply them yet. No data is modified in DP-0005.

DP-0006 adds deterministic cleaning rule selection and cleaned preview:

- `POST /files/apply-cleaning-preview` multipart endpoint
- CSV, TSV, TXT, XLSX, and compatible XLS cleaning preview
- Optional `sheet_name` form field for Excel selected-sheet cleaning
- Cleaning rules for trimming whitespace, normalizing missing tokens, cleaning numeric values, cleaning date values, standardizing category text, recalculating recognized line totals, removing empty rows, removing duplicate rows, dropping empty columns, standardizing column names, and generating missing column names
- Before/after row and column summaries
- Rule effects with applied/no-effect status and affected row/column counts
- Sample-based cleaned preview capped at 20 rows
- Frontend rule selection cards, recommended badges from detected issues, cleaning summary cards, rule effects, and cleaned preview table

DataPulse generates a preview only in DP-0006. It does not modify the original uploaded file and does not provide CSV download/export yet.

DP-0007 adds cleaned CSV export and download:

- `POST /files/export-cleaned-csv` multipart endpoint
- CSV, TSV, TXT, XLSX, and compatible XLS cleaned export
- Optional `sheet_name` form field for Excel selected-sheet export
- Full uploaded CSV-like file export within the existing 10 MB upload limit
- Selected Excel sheet values-only export as CSV
- UTF-8 comma-delimited CSV output with safe quoting for commas, quotes, and newlines
- Safe `Content-Disposition` filenames ending in `_cleaned.csv`
- Frontend export panel, download action, loading state, success state, and error state

Export is CSV-first. DataPulse does not export XLSX and does not preserve Excel formatting, formulas as formulas, merged cell behavior, charts, or pivot tables.

DP-0008 adds professional HTML cleaning reports:

- `POST /files/cleaning-report.html` multipart endpoint
- CSV, TSV, TXT, XLSX, and compatible XLS report generation
- Optional `sheet_name` form field for Excel selected-sheet reports
- Standalone HTML report with no external scripts or CDN dependencies
- Report sections for uploaded file metadata, structure summary, quality issues, column profiles, selected cleaning rules, rule effects, before/after cleaning summary, cleaned preview, export notes, and limitations
- Safe HTML escaping for filenames, sheet names, column names, cell values, issue messages, and other user-provided values
- Frontend report panel with Open HTML Cleaning Report action, loading state, success state, and error state

The HTML report summarizes the deterministic workflow. It does not save history, export PDF, export XLSX, preserve Excel formatting, or modify the original uploaded file.

DP-0009 adds local saved cleaning session history:

- SQLite-backed saved cleaning sessions at `backend/data/datapulse.sqlite3`
- `POST /sessions` endpoint for saving metadata-first cleaning session summaries
- `GET /sessions` endpoint for listing compact saved session summaries
- `GET /sessions/{session_id}` endpoint for reviewing saved session detail
- `DELETE /sessions/{session_id}` endpoint for removing local history records
- Frontend Save Cleaning Session action after cleaned preview generation
- Frontend History section with empty state, saved session list, detail view, delete action, and saved preview snapshot display

Saved history stores source metadata, structure summary, quality summary, selected rules, cleaning summary, rule effects, export/report metadata, timestamps, and an optional small cleaned preview snapshot. Original uploaded files are not stored.

DP-0010 adds saved-session HTML report replay:

- `GET /sessions/{session_id}/report.html` endpoint for opening saved HTML reports from history
- Metadata-based report composition from stored saved cleaning session summaries
- Standalone HTML replay reports with saved session ID, source metadata, quality summary, structure summary, selected rules, cleaning summary, rule effects, export metadata, and limitations
- Clear notice that original uploaded files are not stored and saved reports cannot reprocess the original file
- Safe HTML escaping for stored filenames, metadata, issue text, rule effects, and preview snapshot values
- Frontend Open Saved HTML Report action in saved session detail

Saved report replay does not require the original file to be uploaded again. It is metadata-based and cannot regenerate full cleaned CSV output from history.

DP-0011 adds saved rule set restore:

- `GET /sessions/{session_id}/rules` endpoint for retrieving saved selected rules
- Metadata-only rule restore notes that original uploaded files are not stored
- Frontend Reuse Cleaning Rules action in saved session detail
- Restored rule banner in the main workflow
- Restored rules are preselected after a new file is uploaded, structured, and profiled
- Users can edit restored rule selections before generating cleaned preview
- Users can clear restored rules without deleting the saved session

Saved sessions restore only rule sets and helpful context. A fresh upload is required for validation, structure detection, quality analysis, cleaning preview, export, and live reports.

DP-0012 adds named saved workflow templates:

- SQLite-backed workflow templates stored alongside local saved session metadata
- `POST /templates`, `GET /templates`, `GET /templates/{template_id}`, `PATCH /templates/{template_id}`, and `DELETE /templates/{template_id}` endpoints
- `POST /templates/from-session/{session_id}` endpoint for creating templates from saved session rule sets
- Template records with name, optional description, selected cleaning rules, optional source context, and timestamps
- Frontend Save Rule Set as Template action from the current workflow
- Frontend Save Rules as Template action from saved session detail
- Templates section with list, empty state, detail/edit form, rule editor, apply action, and delete action
- Applied template banner in the main workflow
- Template rules are preselected after a new file is uploaded, structured, and profiled
- Users can edit or clear applied template rules without deleting the template

Templates store only reusable cleaning rules and metadata. They do not store original uploaded files, raw source data, cleaned CSV files, or anything that can reprocess data without a fresh upload.

DP-0013 stabilizes the product for portfolio demo readiness:

- Added QA checklist, demo script, portfolio notes, and synthetic demo files
- Added clearer navigation for Workflow, History, and Templates
- Added workflow stage cards from upload through export/report/save
- Improved empty, loading, and backend-down error copy
- Added visible focus states and keyboard-focusable table regions
- Polished responsive behavior for desktop, tablet, and narrow mobile widths
- Stabilized template ordering so recently edited templates appear first

DP-0013 does not add major new product features. It focuses on cohesion, demo clarity, and reliability.

Targeted dirty-data hardening after DP-0013 improves practical cleaning for messy cafe-sales-style datasets:

- Detects placeholder missing values such as `UNKNOWN`, `ERROR`, `N/A`, `NULL`, `nan`, empty strings, and dash values
- Detects invalid values in numeric-like and date-like columns
- Detects repeated category text that can be safely standardized
- Detects recognized sales line-total opportunities when quantity, unit price, and total columns are present
- Adds deterministic rules for normalizing missing tokens, cleaning numeric values, cleaning date values, standardizing category text, and recalculating recognized line totals
- Keeps the behavior generic; rules are not tied to a filename or hardcoded row values

Local ad hoc datasets in `dataset/` are ignored by Git. They can be used for manual QA without adding user data or large external files to the repository.

Professional UI polish after DP-0013 improves deploy readiness and portfolio presentation:

- Adds a calmer workflow-first app shell and branded navigation
- Replaces milestone-heavy hero copy with clear product positioning and honest scope
- Adds a tokenized frontend design system for color, spacing, radius, surfaces, tables, forms, buttons, and focus states
- Adds progress-aware workflow stage cards
- Improves cleaning rule selection, history tables, template tables, empty states, loading states, and destructive action styling
- Updates backend capabilities metadata so it reflects the implemented workflow
- Adds safe environment examples and configurable backend CORS origins for future deployment planning

Stitch UI adoption applies a supplied SaaS platform reference to the existing DataPulse frontend:

- The Stitch ZIP was inspected and mapped in `docs/STITCH_UI_ADOPTION_PLAN.md`.
- The generated package was used as design reference only; the unzipped package and generated artifacts are not committed.
- Adopted concepts include blue/slate product branding, dense dashboard cards, scroll-safe tables, workflow stage hierarchy, SaaS navigation, rule-set panels, history summaries, and template library styling.
- Rejected concepts include fake admin/account/cloud surfaces, external CDN dependencies, unrelated enterprise claims, and any copy that implies AI cleaning, cloud sync, deployment, PDF export, XLSX export, or Excel formatting preservation.
- Existing upload, structure detection, quality profiling, cleaning preview, CSV export, HTML reports, local history, saved report replay, rule restore, and workflow template features remain the functional source of truth.

## Planned Product Flow

1. Upload a messy CSV, TSV, text table, or Excel file.
2. Validate the file and detect its format.
3. Detect table structure and available Excel sheets.
4. Preview raw data.
5. Detect issues such as missing values, duplicate rows, empty columns, messy headers, and inconsistent types.
6. Select deterministic cleaning rules.
7. Preview cleaned data.
8. Download cleaned CSV.
9. Open a professional HTML cleaning report.
10. Review saved cleaning history.
11. Open saved HTML reports from local history.
12. Reuse saved cleaning rule sets on a newly uploaded file.
13. Save and apply named workflow templates on future uploads.
14. Run a guided local portfolio demo with synthetic files and a QA checklist.

## Current Limitations

- File upload validation exists, but files are not parsed or stored permanently
- CSV/TSV/TXT structure detection and bounded raw preview exist
- Excel sheet discovery and selected sheet raw preview exist for table-like workbooks
- Data quality profiling exists and is sample-based
- Deterministic cleaning preview exists and is sample-based
- Cleaned CSV export exists for CSV-like files and selected Excel sheets
- HTML cleaning report generation exists
- Local SQLite saved cleaning history exists
- Saved-session HTML report replay exists
- Saved rule set restore exists
- Named workflow templates exist
- Product demo materials and QA checklist exist
- Original uploaded files are not stored in history
- Saved reports cannot reprocess original files
- Saved rule sets require a fresh upload before real processing/export
- Templates store rule sets and metadata only
- Templates require a fresh upload before processing/export
- No cloud sync
- No PDF export
- No XLSX export
- No risky type conversion rules yet
- No AI or LLM cleaning
- No authentication
- No deployment

Excel support focuses on table-like sheets. DataPulse does not preserve workbook formatting, formulas as formulas, charts, merged-cell behavior, macros, pivot tables, or presentation styling. Cleaned export remains CSV-first.

DataPulse is deploy-ready in the sense that local build/test commands, environment variables, CORS configuration, ignored local data, and limitations are documented. It has not been deployed by this repository.

## Tech Stack

- Backend: Python, FastAPI, Pydantic, Pytest
- Frontend: React, TypeScript, Vite, Vitest
- Planned data processing: pandas, openpyxl for `.xlsx`, xlrd for `.xls`, Python csv module
- Persistence: local SQLite for saved cleaning session metadata and workflow templates

## Local Setup

Install backend dependencies:

```bash
cd backend
python3 -m pip install -e ".[dev]"
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

## Run Locally

Optional environment setup:

```bash
cp .env.example .env
```

Backend API:

```bash
cd backend
python3 -m uvicorn datapulse_api.main:app --reload
```

Frontend app:

```bash
cd frontend
npm run dev
```

The frontend defaults to `http://127.0.0.1:8000` for API calls. For a different backend URL, set `VITE_API_BASE_URL` before running or building the frontend.

The backend defaults CORS to `http://localhost:5173` and `http://127.0.0.1:5173`. For future hosted frontends, set `DATAPULSE_CORS_ORIGINS` to a comma-separated list of allowed origins.

## Demo Walkthrough

Primary demo path:

1. Start backend and frontend.
2. Upload `demo/messy_sales.csv`.
3. Validate upload.
4. Detect structure and show raw preview.
5. Analyze data quality.
6. Select cleaning rules and generate cleaned preview.
7. Download cleaned CSV.
8. Open live HTML report.
9. Save the cleaning session.
10. Open History, view detail, and open saved HTML report.
11. Reuse saved rules on `demo/messy_students.tsv`.
12. Create, edit, apply, and delete a workflow template.

Detailed script: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)

QA checklist: [docs/QA_CHECKLIST.md](docs/QA_CHECKLIST.md)

Portfolio talking points: [docs/PORTFOLIO_NOTES.md](docs/PORTFOLIO_NOTES.md)

## Testing

Run backend tests:

```bash
make backend-test
```

Run frontend tests:

```bash
make frontend-test
```

Build frontend:

```bash
make frontend-build
```

Run the full foundation check:

```bash
make check
```

Whitespace check:

```bash
git diff --check
```

## API Foundation

Health check:

```http
GET /health
```

Capabilities metadata:

```http
GET /cleaning/capabilities
```

Upload validation:

```http
POST /files/validate-upload
Content-Type: multipart/form-data
```

The upload validation endpoint accepts one `file` field and returns structured metadata:

- Original and sanitized filename
- Detected extension
- Content type
- File size
- Supported/rejected status
- Validation messages
- Next step metadata
- `structure_detection_available: false`

Structure detection and raw preview:

```http
POST /files/detect-structure
Content-Type: multipart/form-data
```

The structure detection endpoint accepts one `file` field. It supports `.csv`, `.tsv`, and `.txt` files, returns delimiter/header/column metadata, bounded preview rows, and structured warnings.

For Excel workbooks, the same endpoint supports two modes:

- Without `sheet_name`: returns workbook sheet discovery metadata.
- With `sheet_name`: returns selected sheet header/column metadata, warnings, and bounded raw preview rows.

Data quality profiling:

```http
POST /files/detect-quality
Content-Type: multipart/form-data
```

The quality endpoint accepts one `file` field and an optional `sheet_name` field for Excel workbooks. It returns issue summaries, severity counts, a heuristic quality score, column-level profiles, and suggested future cleaning rules. Suggested rules are metadata only; DataPulse does not clean, export, or persist the uploaded file in DP-0005.

Cleaning preview:

```http
POST /files/apply-cleaning-preview
Content-Type: multipart/form-data
```

The cleaning preview endpoint accepts one `file` field, a `rules` form field containing selected rule codes, and an optional `sheet_name` for Excel workbooks. It returns before/after summaries, rule effects, warnings, and a bounded cleaned preview. It does not download/export CSV files and does not modify the original uploaded file.

Cleaned CSV export:

```http
POST /files/export-cleaned-csv
Content-Type: multipart/form-data
```

The cleaned CSV export endpoint accepts one `file` field, a `rules` form field containing selected rule codes, and an optional `sheet_name` for Excel workbooks. It returns a downloadable UTF-8 CSV file with a safe `_cleaned.csv` filename. CSV, TSV, and TXT exports process the uploaded file within the existing size limit. Excel exports process selected sheet values only.

HTML cleaning report:

```http
POST /files/cleaning-report.html
Content-Type: multipart/form-data
```

The report endpoint accepts one `file` field, a `rules` form field containing selected rule codes, and an optional `sheet_name` for Excel workbooks. It returns standalone `text/html; charset=utf-8` content with structure, quality, cleaning, export, and limitation sections. User-provided values are HTML-escaped, and the report does not include external scripts or CDN assets.

Saved cleaning sessions:

```http
POST /sessions
GET /sessions
GET /sessions/{session_id}
DELETE /sessions/{session_id}
```

The sessions API stores and returns metadata-first cleaning history from completed workflows. It does not require the original upload, does not store uploaded source files, and keeps history local to the backend SQLite database.

Saved session HTML report replay:

```http
GET /sessions/{session_id}/report.html
```

The saved report endpoint returns standalone `text/html; charset=utf-8` content generated from stored session metadata. It does not require file re-upload, does not reprocess the original file, and clearly states that original uploaded files are not stored.

Saved session rule sets:

```http
GET /sessions/{session_id}/rules
```

The saved rule set endpoint returns selected cleaning rules and metadata-only notes. It does not return uploaded file content and states that a new upload is required before applying restored rules.

Workflow templates:

```http
POST /templates
GET /templates
GET /templates/{template_id}
PATCH /templates/{template_id}
DELETE /templates/{template_id}
POST /templates/from-session/{session_id}
```

The templates API stores named reusable rule sets in local SQLite. Templates include a name, optional description, selected cleaning rules, optional source context, and timestamps. They do not store original files or raw data, and applying a template still requires a fresh upload before cleaning, export, or report generation.

The capabilities endpoint reports supported formats, implemented workflow capabilities, implemented cleaning rule codes, planned rule concepts, export strategy, and current limitations.
