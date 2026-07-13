# DataPulse System Architecture

## Overview

DataPulse is structured as a full-stack application with a FastAPI backend and a React frontend. DP-0006 adds deterministic cleaning rule selection and cleaned preview while keeping CSV download, full-file export, reports, and saved history out of scope.

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

Domain contracts live under `datapulse_api.models`. File validation logic lives in `datapulse_api.services.file_validation`, keeping route handlers thin. The upload validation endpoint reads uploaded bytes to determine file size, returns structured validation metadata, and does not store files permanently.

CSV-like structure detection logic lives in `datapulse_api.services.csv_structure_detection`. It uses bounded byte sampling, Python's csv module, deterministic delimiter scoring, simple header heuristics, row-width normalization for preview display, and structured warnings.

Excel structure detection logic lives in `datapulse_api.services.excel_structure_detection`. It uses `openpyxl` for `.xlsx`, `xlrd` for compatible `.xls`, bounded row sampling, deterministic header heuristics, selected sheet metadata, preview normalization, and structured warnings. Excel previews are values-only.

Data quality profiling logic lives in `datapulse_api.services.data_quality`. It reuses structure detection metadata, reads bounded quality samples, and reports issues without modifying data. CSV-like files can be profiled directly. Excel files require `sheet_name` so the service profiles one selected table-like sheet at a time.

Cleaning preview logic lives in `datapulse_api.services.cleaning_engine`. It reuses bounded table samples, applies only selected deterministic rules, returns before/after summaries, reports rule effects, and generates a capped cleaned preview. It does not store files, mutate uploads, or export cleaned CSV in DP-0006.

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

## Frontend

The frontend is a Vite React application written in TypeScript. The upload workspace supports validation, structure detection, Excel sheet selection, raw preview, quality analysis, issue summary cards, rule selection cards, cleaned preview summaries, rule effects, and scroll-safe preview tables. It does not display download actions or claims of Excel formatting preservation.

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
10. Persist session history in SQLite.

## Architectural Boundaries

- API routes should handle HTTP concerns only.
- Services should own validation, profiling, cleaning, export, and report workflows.
- Models should describe stable contracts and avoid hidden side effects.
- Frontend state should consume backend contracts rather than duplicating cleaning logic.

## Non-Goals

- No AI or LLM cleaning
- No authentication in early versions
- No cloud database
- No deployment in DP-0006
- No OCR, PDF support, or image processing
- No Excel formatting preservation
- No permanent upload storage
- No cleaned CSV download, full-file export, report generation, or saved history
