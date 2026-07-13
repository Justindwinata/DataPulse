# DataPulse

DataPulse is a deterministic messy CSV and Excel cleaner studio. It helps users prepare table-like files for analysis through transparent validation, profiling, rule-based cleaning, preview, CSV-first export, and cleaning reports.

DataPulse is not an AI cleaning tool and does not claim perfect automatic cleaning. The product direction is deliberately rule-based: users should be able to see what was detected, choose which transformations to apply, and review what changed.

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

## Current Limitations

- File upload validation exists, but files are not parsed or stored permanently
- CSV/TSV/TXT structure detection and bounded raw preview exist
- Excel sheet discovery and selected sheet raw preview exist for table-like workbooks
- No full data quality profiling yet
- No cleaning engine yet
- No cleaned CSV export yet
- No HTML report yet
- No saved history yet
- No AI or LLM cleaning
- No authentication
- No deployment

Excel support focuses on table-like sheets. DataPulse does not preserve workbook formatting, formulas as formulas, charts, merged-cell behavior, macros, pivot tables, or presentation styling. Cleaned export remains CSV-first and is planned for a later milestone.

## Tech Stack

- Backend: Python, FastAPI, Pydantic, Pytest
- Frontend: React, TypeScript, Vite, Vitest
- Planned data processing: pandas, openpyxl for `.xlsx`, xlrd for `.xls`, Python csv module
- Planned persistence: SQLite

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

The capabilities endpoint is roadmap-oriented. It lists planned formats and cleaning rules, while clearly stating that parsing, cleaning, export, reports, and history are not implemented yet.
