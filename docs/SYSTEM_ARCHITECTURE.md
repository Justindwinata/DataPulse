# DataPulse System Architecture

## Overview

DataPulse is structured as a full-stack application with a FastAPI backend, local SQLite persistence, and a React frontend. DP-0012 adds named saved workflow templates while keeping uploaded source-file storage, raw source data storage, template-based reprocessing without a fresh upload, cloud sync, authentication, deployment, PDF export, and XLSX export out of scope.

## Repository Layout

```text
DataPulse/
  backend/
    pyproject.toml
    src/datapulse_api/
      api/
      core/
      models/
      services/
    tests/
  frontend/
    package.json
    src/
  docs/
  Makefile
  README.md
  CHANGELOG.md
```

## Backend

The backend exposes API routes through FastAPI. Current endpoints:

- `GET /health`
- `GET /cleaning/capabilities`
- `POST /files/validate-upload`
- `POST /files/detect-structure`
- `POST /files/detect-quality`
- `POST /files/apply-cleaning-preview`
- `POST /files/export-cleaned-csv`
- `POST /files/cleaning-report.html`
- `POST /sessions`
- `GET /sessions`
- `GET /sessions/{session_id}`
- `GET /sessions/{session_id}/report.html`
- `GET /sessions/{session_id}/rules`
- `DELETE /sessions/{session_id}`
- `POST /templates`
- `GET /templates`
- `POST /templates/from-session/{session_id}`
- `GET /templates/{template_id}`
- `PATCH /templates/{template_id}`
- `DELETE /templates/{template_id}`

Domain contracts live under `datapulse_api.models`. File validation logic lives in `datapulse_api.services.file_validation`, keeping route handlers thin. The upload validation endpoint reads uploaded bytes to determine file size, returns structured validation metadata, and does not store files permanently.

CSV-like structure detection logic lives in `datapulse_api.services.csv_structure_detection`. It uses bounded byte sampling, Python's csv module, deterministic delimiter scoring, simple header heuristics, row-width normalization for preview display, and structured warnings.

Excel structure detection logic lives in `datapulse_api.services.excel_structure_detection`. It uses `openpyxl` for `.xlsx`, `xlrd` for compatible `.xls`, bounded row sampling, deterministic header heuristics, selected sheet metadata, preview normalization, and structured warnings. Excel previews are values-only.

Data quality profiling logic lives in `datapulse_api.services.data_quality`. It reuses structure detection metadata, reads bounded quality samples, and reports issues without modifying data. CSV-like files can be profiled directly. Excel files require `sheet_name` so the service profiles one selected table-like sheet at a time.

Cleaning preview logic lives in `datapulse_api.services.cleaning_engine`. It reuses bounded table samples, applies only selected deterministic rules, returns before/after summaries, reports rule effects, and generates a capped cleaned preview. It does not store files, mutate uploads, or export cleaned CSV in DP-0006.

Cleaned CSV export logic lives in `datapulse_api.services.cleaned_csv_export`. It applies the same deterministic selected rules and returns UTF-8 CSV bytes with safe quoting. CSV-like inputs are exported from the uploaded file within the existing 10 MB limit. Excel inputs export selected sheet values only and require `sheet_name`.

Cleaning report composition lives in `datapulse_api.services.cleaning_report`. It reuses structure detection, data quality profiling, cleaning preview, and cleaned CSV export metadata to build one report document. HTML rendering lives in `datapulse_api.services.report_html`; it returns standalone HTML with inline CSS, no JavaScript, no external CDN assets, and escaped user-provided values.

Saved cleaning session persistence lives in `datapulse_api.services.session_repository`. SQLite connection and schema initialization live in `datapulse_api.core.database`. The default local database path is `backend/data/datapulse.sqlite3`, and the database file is ignored by Git. Session history stores structured metadata and optional small preview snapshots; it does not store original uploaded files.

Saved session report composition lives in `datapulse_api.services.saved_session_report`. It converts `SavedCleaningSessionDetail` metadata into a report document without requiring file re-upload or attempting full data reprocessing. Saved report rendering reuses `datapulse_api.services.report_html` styling and escaping utilities while clearly marking reports as metadata-based.

Saved rule set restore uses the selected rule codes stored in saved cleaning session metadata. The `GET /sessions/{session_id}/rules` endpoint returns rule codes and explicit notes that original files are not stored and a new upload is required before applying restored rules.

Workflow template persistence lives in `datapulse_api.services.template_repository`. Templates are local SQLite records stored in the same app database as saved sessions. They store a name, optional description, selected rule codes, optional source session/file context, and timestamps. Templates do not store original uploaded files, raw source rows, cleaned CSV content, or data needed to reprocess a file without a fresh upload.

Current upload validation rules:

- Supported extensions: `.csv`, `.tsv`, `.txt`, `.xlsx`, `.xls`
- Maximum size: 10 MB
- Empty files are rejected
- Unsupported extensions are rejected
- Unsafe path-like filenames are sanitized for safe display
- Structure detection is explicitly reported as unavailable in DP-0002

Current CSV-like structure detection rules:

- Supported extensions: `.csv`, `.tsv`, `.txt`
- Delimiter candidates: comma, semicolon, tab, pipe
- Preview rows are capped at 20
- Sample rows are capped and do not imply full-file row count
- Warning codes describe messy structure without cleaning the data

Current Excel structure detection rules:

- Supported extensions: `.xlsx`, `.xls`
- Workbook discovery returns sheet names, sheet count, default sheet, and sheet metadata
- Selected sheet preview requires `sheet_name`
- Preview rows are capped at 20
- Detection rows are sampled and do not imply full workbook profiling
- Formatting, formulas as formulas, merged cell behavior, charts, pivot tables, macros, and styling are not preserved

Current data quality profiling rules:

- Supported inputs: `.csv`, `.tsv`, `.txt`, `.xlsx`, `.xls`
- Excel profiling requires a selected sheet name
- Profiling is bounded and sample-based
- Issue detection includes missing values, empty rows, empty columns, duplicate rows, duplicate headers, missing headers, messy headers, inconsistent row widths, leading/trailing whitespace, mixed type values, numeric-looking text, date-looking text, and high-missing columns
- Column profiles include missing counts, missing percentage, inferred type, unique count, sample values, and issue codes
- Quality score starts at 100 and subtracts deterministic points by severity: critical issues cost more than warnings, warnings cost more than info notes
- Suggested cleaning rules are returned as future-rule metadata only

Current cleaning preview rules:

- `trim_whitespace`
- `remove_empty_rows`
- `remove_duplicate_rows`
- `drop_empty_columns`
- `standardize_column_names`
- `generate_missing_column_names`

Cleaning preview is sample-based. Numeric conversion, date conversion, boolean conversion, and missing-value imputation are intentionally deferred because they can change data meaning.

Current cleaned CSV export rules:

- Output format is CSV only
- Encoding is UTF-8
- Delimiter is comma
- CSV quoting is handled by Python's csv module
- Exported filenames are sanitized and end with `_cleaned.csv`
- Excel export is values-only and does not preserve workbook formatting

Current HTML report rules:

- Output format is standalone HTML
- Content type is `text/html; charset=utf-8`
- Report generation requires `sheet_name` for Excel files
- Sections include header metadata, executive summary, structure summary, quality issues, column profiles, selected rules, rule effects, cleaning summary, cleaned preview, export summary, and limitations
- Filenames, sheet names, column names, cell values, issue messages, and other dynamic values are escaped before rendering
- No external scripts, JavaScript, or CDN assets are included

Current saved history rules:

- Persistence is local SQLite only
- Database path is `backend/data/datapulse.sqlite3`
- Stored records are metadata-first session summaries
- Original uploaded files are not stored
- Stored fields include source metadata, selected sheet name, structure summary, quality summary, selected rules, cleaning summary, rule effects, export summary, report summary, optional cleaned preview snapshot, and timestamps
- API supports create, list, detail, and delete operations
- Saved session report replay is available at `GET /sessions/{session_id}/report.html`
- Saved report replay is metadata-based and cannot reprocess the original file
- Saved rule set restore is available at `GET /sessions/{session_id}/rules`
- Saved rule sets restore selected rule codes only
- A fresh upload is required before restored rules can be applied to data
- Tests use temporary database paths instead of the local app database

Current workflow template rules:

- Persistence is local SQLite only
- Templates store rule sets and metadata only
- Required fields are template name and at least one supported cleaning rule
- Optional fields include description, source session ID, and source filename context
- API supports create, list, detail, update, delete, and create-from-session operations
- Create-from-session copies selected rule codes from saved session metadata without storing original files
- Applying a template only preselects rules in the frontend workflow
- A fresh upload is required before template rules can be used for validation, structure detection, quality analysis, cleaning preview, export, or live reports
- Tests use temporary database paths instead of the local app database

Current saved report replay rules:

- Output format is standalone HTML
- Content type is `text/html; charset=utf-8`
- Reports include saved session ID, source filename, file type, selected sheet, session timestamps, replay timestamp, executive summary, structure metadata, quality metadata, selected rules, cleaning summary, rule effects, preview snapshot, export metadata, and limitations
- Stored values are escaped before rendering
- Original uploaded files are not required and are not stored
- Saved reports cannot regenerate full cleaned CSV output from history

## Frontend

The frontend is a Vite React application written in TypeScript. The upload workspace supports validation, structure detection, Excel sheet selection, raw preview, quality analysis, restored/template rule banners, issue summary cards, rule selection cards, cleaned preview summaries, rule effects, cleaned CSV download, HTML report opening, saved session creation, template creation from current rules, and scroll-safe preview tables. The History section lists saved sessions, displays metadata-first detail, shows optional saved preview snapshots, supports saved HTML report replay, supports saved rule set restore, supports template creation from saved session rules, and supports local delete actions. The Templates section lists named templates, supports detail/edit, applies template rules to the current workflow, and deletes local template records.

## Future Processing Flow

1. Validate uploaded file metadata and extension.
2. Detect file type and table structure.
3. For Excel files, list available sheets.
4. Generate a bounded raw preview.
5. Detect structural and data quality issues.
6. Apply user-selected deterministic cleaning rules.
7. Generate cleaned preview and cleaning summary.
8. Export cleaned CSV.
9. Generate an HTML report.
10. Persist metadata-first session history in SQLite.
11. Replay saved HTML reports from stored metadata.
12. Reuse saved rule sets on a newly uploaded file.
13. Save, manage, and apply named workflow templates to future uploads.

## Architectural Boundaries

- API routes should handle HTTP concerns only.
- Services should own validation, profiling, cleaning, export, and report workflows.
- Models should describe stable contracts and avoid hidden side effects.
- Frontend state should consume backend contracts rather than duplicating cleaning logic.

## Non-Goals

- No AI or LLM cleaning
- No authentication in early versions
- No cloud database
- No deployment in DP-0012
- No OCR, PDF support, or image processing
- No Excel formatting preservation
- No permanent upload storage
- No original uploaded file storage in saved history
- No original uploaded file storage in workflow templates
- No raw source data storage in workflow templates
- No cloud sync
- No PDF export
- No XLSX export
