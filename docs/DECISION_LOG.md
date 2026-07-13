# Decision Log

## 2026-07-12 - DP-0001 Product Positioning

DataPulse will be a deterministic, rule-based CSV and Excel cleaner studio. It will not be positioned as an AI product and will not claim perfect automatic cleaning.

## 2026-07-12 - CSV-First Export Strategy

Cleaned output will prioritize CSV export because CSV is portable, analysis-friendly, and easier to reason about than preserving spreadsheet formatting.

## 2026-07-12 - No Docker in Initial Foundation

DP-0001 will avoid Docker to keep the local development path simple for a portfolio foundation.

## 2026-07-12 - FastAPI and React Foundation

The initial stack uses FastAPI, Pydantic, Pytest, React, TypeScript, Vite, and Vitest. This stack keeps the project understandable, testable, and familiar for a GitHub portfolio.

## 2026-07-12 - Capabilities Metadata Before Processing

DP-0001 exposes a capabilities endpoint before implementing upload or cleaning. The endpoint is intentionally honest: it documents planned formats and rules while stating that processing features are not implemented yet.

## 2026-07-12 - Upload Validation Before Parsing

DP-0002 validates only file metadata, extension, and size. It deliberately avoids CSV parsing, Excel sheet inspection, delimiter detection, and header detection so the first intake milestone stays safe and testable.

## 2026-07-12 - No Permanent Uploaded File Storage

Uploaded files are read for validation and not stored permanently. Future contracts may add temporary session handling, but DP-0002 keeps persistence out of scope.

## 2026-07-12 - CSV-Like Structure Detection Before Excel

DP-0003 implements structure detection only for CSV, TSV, and TXT files. Excel files return an explicit later-milestone message because workbook sheet discovery requires a separate implementation path.

## 2026-07-12 - Bounded Preview Over Full-File Parsing

Structure detection reads bounded samples and returns capped preview rows. Full-file row counts, profiling, cleaning, and export are deferred to later milestones to avoid overbuilding and unsafe memory behavior.

## 2026-07-13 - Excel Preview Is Values-Only

DP-0004 treats Excel workbooks as sources of table-like values. It does not preserve formatting, formulas as formulas, merged cell behavior, charts, pivot tables, macros, or workbook styling.

## 2026-07-13 - Sheet Selection Before Excel Preview

Excel workbook discovery and sheet preview are separate steps. The first call returns sheet metadata; a second call with `sheet_name` returns bounded raw preview for the selected sheet.

## 2026-07-13 - Quality Profiling Before Cleaning

DP-0005 detects data quality issues before introducing any cleaning engine. The service reports issues, column profiles, suggested future cleaning rules, and a transparent heuristic score, but it does not modify uploaded data.

## 2026-07-13 - Heuristic Quality Score Is Sample-Based

The quality score starts at 100 and subtracts deterministic points by issue severity. It is a practical diagnostic signal for the sampled data, not a scientific or full-file guarantee.

## 2026-07-13 - Cleaning Preview Before Export

DP-0006 applies selected deterministic rules to a bounded sample and returns a cleaned preview with rule effects. It intentionally does not implement CSV download yet so users can inspect transformations before export is introduced.

## 2026-07-13 - Defer Risky Type Conversions

DP-0006 avoids numeric, date, boolean, and missing-value conversion rules. Those transformations can change meaning, so they should be designed as separate explicit rules with stronger previews and reporting.

## 2026-07-13 - CSV Export Before Reports

DP-0007 implements CSV download before HTML reports or saved history. This keeps the product focused on the core analyst workflow: validate, inspect, clean deterministically, and export an analysis-ready CSV.

## 2026-07-13 - Excel Export Is Values-Only CSV

Excel inputs export selected sheet values as CSV. DataPulse does not preserve formatting, formulas as formulas, merged cell behavior, charts, pivot tables, macros, or workbook styling.

## 2026-07-14 - HTML Report Before Saved History

DP-0008 generates standalone HTML reports before adding persistence. Users can review a complete cleaning workflow summary without creating accounts, storing uploads, or introducing a database.

## 2026-07-14 - Escape Report Data by Default

HTML reports escape filenames, sheet names, column names, cell values, issue messages, and other dynamic values before rendering. Reports do not include external scripts or CDN assets.
