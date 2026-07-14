# DataPulse Portfolio Notes

## Problem Solved

Messy CSV and Excel exports often need repeatable cleanup before analysis. DataPulse helps users inspect structure, detect data quality issues, apply deterministic cleaning rules, export cleaned CSV files, and keep local metadata-first history.

## Technical Highlights

- FastAPI backend with Pydantic contracts and Pytest coverage.
- React, TypeScript, Vite frontend with Vitest coverage.
- Deterministic CSV/TSV/TXT delimiter and header detection.
- Excel workbook sheet discovery and selected sheet preview.
- Rule-based cleaning engine with transparent before/after summaries.
- UTF-8 CSV export with safe quoting and filenames.
- Standalone HTML report rendering with escaped dynamic values.
- Local SQLite persistence for saved cleaning sessions and workflow templates.
- Metadata-only saved report replay and reusable rule/template workflows.

## Architecture

DataPulse keeps API routes thin and moves product logic into services:

- Validation: file extension, size, empty-file rejection, safe filenames.
- Structure detection: CSV-like parsing and Excel sheet sampling.
- Quality profiling: sample-based issue detection and column profiles.
- Cleaning: selected deterministic rules only.
- Export/reporting: CSV-first export and standalone HTML.
- Persistence: local SQLite metadata for sessions and templates.

## Portfolio Positioning

DataPulse demonstrates full-stack product engineering rather than a toy CRUD app. It shows backend contracts, file handling, data processing, frontend workflow design, local persistence, documentation, and test discipline.

## Honest Limitations

- Local-only app.
- Original uploaded files are not stored.
- Saved history and templates are local SQLite only.
- No cloud sync or authentication.
- No PDF export or XLSX export.
- Excel formatting, formulas, merged cell behavior, charts, and pivot tables are not preserved.
- No risky type conversion rules yet.
- No AI/LLM cleaning.
- No deployment workflow.

## Future Work

- Stronger keyboard accessibility pass.
- Template search and filtering.
- Optional template JSON import/export.
- Safer large-file streaming.
- More explicit numeric/date conversion rules with previews.
- Optional deployment after local product scope is stable.
