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
- DP-0006: deterministic cleaning rule selection and sample-based cleaned preview.
- DP-0007: cleaned CSV export and frontend download workflow.
- DP-0008: standalone HTML cleaning report generation and frontend report opening workflow.
- DP-0009: local SQLite saved cleaning session history, metadata-first session detail, and frontend History workflow.
- DP-0010: saved-session HTML report replay from local history without original file re-upload.
- DP-0011: saved rule set restore for applying prior rule selections to a newly uploaded file.
- DP-0012: named workflow templates for saving, editing, applying, and deleting reusable cleaning rule sets.

## Cleaning Model

Cleaning is rule-based and deterministic. Current cleaning rules include trimming whitespace, removing empty rows, removing duplicate rows, dropping fully empty columns, standardizing column names, and generating missing column names. Future rules may include promoting a detected header row, normalizing text casing, and carefully converting numeric or date columns.

## Limitations

CSV and Excel cleaning is inherently contextual. A tool can detect likely issues, but the user should confirm transformations because some "messy" values may be meaningful for a specific dataset.

DP-0006 cleaned preview is bounded and sample-based. It can show likely cleaning effects, but it does not export CSV files, generate reports, save history, or claim the full file has been cleaned.

DP-0007 exports cleaned CSV files from selected deterministic rules. CSV-like inputs are processed from the uploaded file within the existing size limit. Excel inputs export selected sheet values only; workbook formatting and spreadsheet-specific behavior are not preserved.

DP-0008 generates standalone HTML reports from uploaded data and selected deterministic rules. Reports summarize structure, quality, selected rules, rule effects, cleaning summaries, cleaned preview, export notes, and limitations. Reports escape user-provided values and do not save history, export PDF, export XLSX, or preserve Excel formatting.

DP-0009 stores saved cleaning session metadata in local SQLite. History records include source metadata, selected sheet name, structure summary, quality summary, selected rules, cleaning summary, rule effects, export/report metadata, timestamps, and an optional small cleaned preview snapshot. Original uploaded files are not stored, history is not cloud-synced, and saved records do not replace the need to review source data before future exports.

DP-0010 generates saved-session HTML reports from stored metadata. Reports are useful for reviewing prior cleaning decisions without re-uploading the original file. They cannot reprocess the original file, regenerate full cleaned CSV output from history, or claim that the saved snapshot represents the full source dataset.

DP-0011 restores selected cleaning rule codes from saved sessions. Restored rules are preselected only after a new file is uploaded, structured, and profiled. Users can edit or clear restored rules. Saved sessions do not restore files, reprocess saved data, regenerate cleaned CSV, or create full live reports from old uploads.

DP-0012 stores named workflow templates in local SQLite. Templates include a name, optional description, selected cleaning rules, optional source context, and timestamps. Users can create templates from the current workflow or saved session rules, edit template metadata and rules, delete templates, and apply a template to preselect rules for a newly uploaded file. Templates do not store original uploaded files, raw source data, cleaned CSV files, or anything that can process/export data without a fresh upload.
