# DataPulse System Architecture

## Overview

DataPulse is structured as a full-stack application with a FastAPI backend and a React frontend. DP-0001 focuses on clean boundaries and contracts before implementing the cleaning engine.

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

Domain contracts live under `datapulse_api.models`. Future parsing and cleaning orchestration should live in services rather than route handlers.

## Frontend

The frontend is a Vite React application written in TypeScript. DP-0001 provides a portfolio-ready product shell that communicates the planned workflow without pretending the full workflow is implemented.

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
- No deployment in DP-0001
- No OCR, PDF support, or image processing
- No Excel formatting preservation
