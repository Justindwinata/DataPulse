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
