# DataPulse

DataPulse is a deterministic messy CSV and Excel cleaner studio. It helps users prepare table-like files for analysis through transparent validation, profiling, rule-based cleaning, preview, CSV-first export, and cleaning reports.

DataPulse is not an AI cleaning tool and does not claim perfect automatic cleaning. The product direction is deliberately rule-based: users should be able to see what was detected, choose which transformations to apply, and review what changed.

## DP-0001 Scope

DP-0001 establishes the product and engineering foundation:

- FastAPI backend package with service metadata and `GET /health`
- `GET /cleaning/capabilities` metadata endpoint
- Pydantic domain contracts for the future cleaning workflow
- React, TypeScript, Vite frontend foundation
- Vitest and Pytest tests from the beginning
- Root Makefile for repeatable local checks
- Product requirements, architecture notes, roadmap, decision log, and changelog

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

- No actual file upload yet
- No CSV parsing yet
- No Excel parsing yet
- No cleaning engine yet
- No cleaned CSV export yet
- No HTML report yet
- No saved history yet
- No AI or LLM cleaning
- No authentication
- No deployment

Excel support will focus on table-like sheets. DataPulse does not aim to preserve workbook formatting, formulas, charts, merged-cell layouts, macros, or presentation styling. Cleaned export is CSV-first.

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

The capabilities endpoint is roadmap-oriented. It lists planned formats and cleaning rules, while clearly stating that upload, parsing, cleaning, export, reports, and history are not implemented in DP-0001.
