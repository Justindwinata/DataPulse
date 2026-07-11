# DataPulse System Architecture

## Overview

DataPulse is structured as a full-stack application with a FastAPI backend and a React frontend. DP-0003 adds CSV-like structure detection and raw preview while keeping Excel parsing and cleaning out of scope.

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

Domain contracts live under `datapulse_api.models`. File validation logic lives in `datapulse_api.services.file_validation`, keeping route handlers thin. The upload validation endpoint reads uploaded bytes to determine file size, returns structured validation metadata, and does not store files permanently.

CSV-like structure detection logic lives in `datapulse_api.services.csv_structure_detection`. It uses bounded byte sampling, Python's csv module, deterministic delimiter scoring, simple header heuristics, row-width normalization for preview display, and structured warnings.

Current upload validation rules:

- Supported extensions: `.csv`, `.tsv`, `.txt`, `.xlsx`, `.xls`
- Maximum size: 10 MB
- Empty files are rejected
- Unsupported extensions are rejected
- Unsafe path-like filenames are sanitized for safe display
- Structure detection is explicitly reported as unavailable in DP-0002

Current CSV-like structure detection rules:

- Supported extensions: `.csv`, `.tsv`, `.txt`
- Excel extensions return a later-milestone limitation
- Delimiter candidates: comma, semicolon, tab, pipe
- Preview rows are capped at 20
- Sample rows are capped and do not imply full-file row count
- Warning codes describe messy structure without cleaning the data

## Frontend

The frontend is a Vite React application written in TypeScript. DP-0003 extends the upload workspace with a Detect Structure action for accepted CSV-like files, structure summary cards, warning panel, and a scroll-safe raw preview table. It does not display fake cleaned data or fake Excel previews.

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
- No deployment in DP-0003
- No OCR, PDF support, or image processing
- No Excel formatting preservation
- No permanent upload storage
- No cleaning engine or export generation
