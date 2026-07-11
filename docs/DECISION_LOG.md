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
