# Changelog

All notable changes to DataPulse will be documented in this file.

## 0.10.0 - DP-0010 Saved Session HTML Report Replay

### Added

- Added saved session report composition service for metadata-based replay reports.
- Added saved session report document contracts.
- Added standalone saved-session HTML renderer using safe escaping and no external scripts.
- Added `GET /sessions/{session_id}/report.html` endpoint.
- Added frontend saved session report client.
- Added Open Saved HTML Report panel in saved session detail.
- Added tests for saved report endpoint behavior, escaping, frontend blob opening, and error states.

### Not Included

- Original uploaded file storage, original file reprocessing from history, cloud sync, authentication, PDF export, XLSX export, risky type conversion rules, AI/LLM cleaning, deployment, or Excel formatting/formula/chart/pivot preservation.

## 0.9.0 - DP-0009 Saved Cleaning Sessions and Local History

### Added

- Added saved cleaning session response models for create, summary, detail, and list workflows.
- Added SQLite persistence foundation for local cleaning session metadata at `backend/data/datapulse.sqlite3`.
- Added deterministic schema initialization and repository methods for create, list, get, and delete operations.
- Added `POST /sessions`, `GET /sessions`, `GET /sessions/{session_id}`, and `DELETE /sessions/{session_id}` endpoints.
- Added frontend saved sessions API client.
- Added Save Cleaning Session workflow after cleaned preview generation.
- Added History section with empty state, saved session list, detail view, delete action, and saved preview snapshot display.

### Not Included

- Original uploaded file storage, cloud sync, authentication, PDF export, XLSX export, risky type conversion rules, AI/LLM cleaning, deployment, or Excel formatting/formula/chart/pivot preservation.

## 0.8.0 - DP-0008 Professional HTML Cleaning Report

### Added

- Added cleaning report composition models and metadata.
- Added standalone HTML report renderer with DataPulse branding, executive summary, structure summary, quality summary, column profile table, cleaning summary, rule effects, cleaned preview, export summary, and limitations.
- Added safe HTML escaping for filenames, sheet names, column names, cell values, issue messages, and report text.
- Added `POST /files/cleaning-report.html` endpoint returning `text/html; charset=utf-8`.
- Added frontend HTML report client.
- Added frontend report panel with Open HTML Cleaning Report action, loading state, opened state, and error state.

### Not Included

- Saved history, PDF export, XLSX export, risky type conversion rules, AI/LLM cleaning, authentication, deployment, or Excel formatting/formula/chart/pivot preservation.

## 0.7.0 - DP-0007 Cleaned CSV Export and Download

### Added

- Added cleaned CSV export service.
- Added full uploaded CSV-like export within the existing upload size limit.
- Added selected Excel sheet values-only export as CSV.
- Added safe UTF-8 CSV rendering with comma delimiter and standard CSV quoting.
- Added `POST /files/export-cleaned-csv` endpoint with safe `Content-Disposition` filename.
- Added frontend cleaned CSV export client.
- Added frontend export panel, Download Cleaned CSV action, loading state, success state, and error state.

### Fixed

- Hardened export edge cases for unsafe filenames, no-rules export, repeated form rules, all-empty columns, and CSV escaping.

### Not Included

- HTML reports, saved history, XLSX export, risky type conversion rules, AI/LLM cleaning, authentication, deployment, or Excel formatting/formula/chart/pivot preservation.

## 0.6.0 - DP-0006 Cleaning Rules Engine and Cleaned Preview

### Added

- Added cleaning preview response models for selected rules, before/after summaries, rule effects, warnings, and cleaned preview rows.
- Added deterministic cleaning engine service.
- Added cleaning rules for trimming whitespace, removing empty rows, removing duplicate rows, dropping empty columns, standardizing column names, and generating missing column names.
- Added `POST /files/apply-cleaning-preview` endpoint with optional `sheet_name`.
- Added sample-based cleaned preview capped at 20 rows.
- Added frontend cleaning preview client.
- Added frontend rule selection cards, recommended rule badges, cleaning summary cards, rule effects, and cleaned preview table.

### Not Included

- Cleaned CSV download, full-file export, HTML reports, saved history, risky type conversion rules, AI/LLM cleaning, authentication, deployment, or Excel formatting/formula/chart/pivot preservation.

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
