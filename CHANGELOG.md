# Changelog

All notable changes to DataPulse will be documented in this file.

## 0.3.0 - DP-0003 CSV Structure Detection and Raw Preview

### Added

- Added structure detection response models and stable warning contracts.
- Added deterministic CSV-like structure detection service.
- Added delimiter detection for comma, semicolon, tab, and pipe.
- Added simple header candidate detection and generated column names.
- Added bounded raw preview for CSV, TSV, and TXT files.
- Added structure warnings for inconsistent row widths, empty rows, duplicate headers, missing headers, leading metadata rows, and very small samples.
- Added `POST /files/detect-structure` endpoint.
- Added frontend structure detection client.
- Added structure summary cards, warning panel, and raw preview table UI.
- Added honest Excel limitation state for `.xlsx` and `.xls`.

### Not Included

- Excel sheet parsing, full data quality profiling, cleaning engine, cleaned CSV export, HTML reports, saved history, AI/LLM cleaning, authentication, and deployment.

## 0.2.0 - DP-0002 File Upload Validation

### Added

- Added upload validation response models and stable validation status contracts.
- Added deterministic backend file validation service.
- Added `POST /files/validate-upload` multipart endpoint.
- Added validation for supported extensions, empty files, file size, and unsafe filenames.
- Added frontend upload validation API client.
- Added upload validation workspace with selected file metadata, validation action, result states, loading state, and backend error state.
- Added tests for backend models, service logic, endpoint behavior, frontend API client, and upload UI.
- Added `make lint` alias for repository format checking.

### Not Included

- CSV parsing, Excel sheet parsing, delimiter detection, header detection, raw preview, cleaning engine, cleaned CSV export, HTML reports, saved history, AI/LLM cleaning, authentication, and deployment.

## 0.1.0 - DP-0001 Foundation

### Added

- Initialized the DataPulse repository foundation.
- Added FastAPI backend with health check.
- Added React, TypeScript, and Vite frontend foundation.
- Added deterministic data cleaning domain contracts.
- Added cleaning capabilities metadata endpoint.
- Added Makefile commands for backend tests, frontend tests, frontend build, and full checks.
- Added product requirements, system architecture, roadmap, and decision log documentation.

### Not Included

- File upload, CSV parsing, Excel parsing, cleaning engine, cleaned export, HTML reports, saved history, AI/LLM cleaning, authentication, and deployment.
