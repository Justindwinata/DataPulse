# DataPulse Product Requirements

## Product Summary

DataPulse is a deterministic CSV and Excel cleaning studio for messy table-like files. It is designed to help analysts, students, data learners, and developers prepare tabular data for analysis without hiding transformations.

## Problem

Messy CSV and spreadsheet files often contain inconsistent headers, blank rows, duplicate rows, empty columns, mixed data types, extra whitespace, and unclear structure. Cleaning these files manually is repetitive and error-prone.

## Target Users

- Students preparing datasets for coursework or portfolio analysis
- Junior analysts cleaning exported reports
- Developers validating tabular files before import
- Data learners who need transparent cleaning steps

## Product Principles

- Deterministic cleaning over opaque automation
- User-selected rules over claims of perfect automatic cleanup
- CSV-first export over spreadsheet formatting preservation
- Clear validation errors and cleaning summaries
- Small, testable product increments

## Planned Supported Formats

- `.csv`
- `.tsv`
- `.txt` table-like files
- `.xlsx`
- `.xls`

Excel support will focus on table-like sheets. DataPulse will not preserve workbook formatting, formulas, charts, macros, or complex visual layouts.

## MVP Scope

The MVP should support file intake, validation, raw preview, issue detection, rule selection, cleaned preview, CSV export, HTML report generation, and local saved history.

## DP-0001 Implementation

DP-0001 implements the engineering foundation only:

- Repository structure
- Backend FastAPI foundation
- Frontend React foundation
- Health check endpoint
- Capabilities metadata endpoint
- Pydantic domain contracts
- Tests and Makefile checks
- Product documentation

## Deferred Work

DP-0001 intentionally does not implement file upload, parsing, cleaning, CSV export, HTML reports, SQLite history, authentication, deployment, AI features, OCR, PDF support, or image processing.

## Current Implemented Milestones

- DP-0001: product foundation, backend/frontend scaffolding, health check, capabilities metadata, and domain contracts.
- DP-0002: upload validation for CSV, TSV, TXT, XLSX, and XLS files.
- DP-0003: CSV, TSV, and TXT structure detection with bounded raw preview.
- DP-0004: Excel workbook sheet discovery and selected sheet values-only preview.
- DP-0005: deterministic sample-based data quality issue detection and column profiling.

## Cleaning Model

Cleaning will be rule-based and deterministic. Example future rules include trimming whitespace, removing empty rows, removing duplicate rows, dropping fully empty columns, standardizing column names, promoting a detected header row, generating missing column names, normalizing text casing, and converting numeric or date columns.

## Limitations

CSV and Excel cleaning is inherently contextual. A tool can detect likely issues, but the user should confirm transformations because some "messy" values may be meaningful for a specific dataset.

DP-0005 quality profiling is bounded and sample-based. It can report likely issues and suggested future cleaning rules, but it does not clean data, create a cleaned preview, export CSV files, generate reports, or save history.
