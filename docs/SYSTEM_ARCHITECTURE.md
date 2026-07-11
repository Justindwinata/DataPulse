# DataPulse System Architecture

## Overview

DataPulse is structured as a full-stack application with a FastAPI backend and a React frontend. DP-0002 adds safe upload validation while keeping parsing and cleaning out of scope.

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

Domain contracts live under `datapulse_api.models`. File validation logic lives in `datapulse_api.services.file_validation`, keeping route handlers thin. The upload validation endpoint reads uploaded bytes to determine file size, returns structured validation metadata, and does not store files permanently.

Current upload validation rules:

- Supported extensions: `.csv`, `.tsv`, `.txt`, `.xlsx`, `.xls`
- Maximum size: 10 MB
- Empty files are rejected
- Unsupported extensions are rejected
- Unsafe path-like filenames are sanitized for safe display
- Structure detection is explicitly reported as unavailable in DP-0002

## Frontend

The frontend is a Vite React application written in TypeScript. DP-0002 provides an upload validation workspace with selected file metadata, validation actions, loading state, accepted/rejected results, and backend error handling. It does not display fake parsing results or cleaned previews.

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
- No deployment in DP-0002
- No OCR, PDF support, or image processing
- No Excel formatting preservation
- No permanent upload storage
