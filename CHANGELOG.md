# Changelog

All notable changes to DataPulse will be documented in this file.

## 0.5.0 - DP-0005 Data Quality Issue Detection

### Added

- Added data quality profiling response models and stable issue severity contracts.
- Added deterministic backend profiling service for CSV-like files and selected Excel sheets.
- Added `POST /files/detect-quality` endpoint with optional `sheet_name`.
- Added sample-based detection for missing values, empty rows, empty columns, duplicate rows, duplicate column names, missing column names, messy column names, inconsistent row widths, leading/trailing whitespace, mixed type values, numeric-looking text, date-looking text, and high-missing columns.
- Added column-level profiles with inferred type, missing counts, missing percentage, unique count, sample values, and issue codes.
- Added transparent heuristic quality score based on issue severity.
- Added frontend data quality client.
- Added quality summary cards, issue cards grouped by severity, and column profile table.

### Not Included

- Cleaning engine, cleaned preview, cleaned CSV export, HTML reports, saved history, AI/LLM cleaning, authentication, deployment, or Excel formatting/formula/chart/pivot preservation.

## 0.4.0 - DP-0004 Excel Sheet Detection and Raw Preview

### Added

- Added Excel workbook metadata and selected sheet response contracts.
- Added `openpyxl` and `xlrd` backend dependencies.
- Added Excel workbook sheet discovery service.
- Added selected Excel sheet bounded raw preview detection.
- Added warnings for empty sheets, empty rows, empty columns, duplicate headers, missing headers, missing selected sheets, sample limits, and Excel preview limitations.
- Integrated Excel workbook discovery and selected sheet preview into `POST /files/detect-structure`.
- Added frontend sheet selector and selected sheet preview workflow.
- Preserved CSV, TSV, and TXT structure detection behavior.

### Not Included

- Full data quality profiling, cleaning engine, cleaned CSV export, HTML reports, saved history, AI/LLM cleaning, authentication, deployment, or Excel formatting/formula/chart/pivot preservation.

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
