# DataPulse Demo Script

This script is for a local portfolio demo.

## 1. Start The App

Run the backend:

```bash
cd backend
python3 -m uvicorn datapulse_api.main:app --reload
```

Run the frontend:

```bash
cd frontend
npm run dev
```

Open the Vite URL, usually `http://127.0.0.1:5173`.

## 2. Upload And Validate

1. In the Workflow section, choose `demo/messy_sales.csv`.
2. Click `Validate upload`.
3. Explain that DataPulse validates extension, size, content type, and filename safety.
4. Point out that uploaded files are not stored permanently.

## 3. Detect Structure

1. Click `Detect Structure`.
2. Show delimiter, column count, header detection, preview rows, and warnings.
3. Explain that CSV-like structure detection is deterministic and bounded.

## 4. Analyze Quality

1. Click `Analyze Data Quality`.
2. Show quality score, issue counts, issue cards, and column profile table.
3. Explain that the score is heuristic and sample-based.

## 5. Generate Cleaned Preview

1. Select:
   - Trim whitespace
   - Remove empty rows
   - Remove duplicate rows
   - Drop empty columns
   - Standardize column names
2. Click `Generate Cleaned Preview`.
3. Show before/after counts and rule effects.
4. Explain that the original uploaded file is not modified.

## 6. Export CSV

1. Click `Download Cleaned CSV`.
2. Open the downloaded CSV if practical.
3. Explain that DataPulse exports cleaned values as CSV and does not export XLSX.

## 7. Open Live HTML Report

1. Click `Open HTML Cleaning Report`.
2. Show structure, quality, selected rules, rule effects, export notes, and limitations.
3. Explain that report values are escaped and the report is standalone HTML.

## 8. Save Session And Replay Report

1. Click `Save Cleaning Session`.
2. Load `History`.
3. Open the saved session detail.
4. Click `Open Saved HTML Report`.
5. Explain that saved report replay is metadata-based and does not require the original file.

## 9. Reuse Rules

1. In History detail, click `Reuse Cleaning Rules`.
2. Return to Workflow.
3. Explain that only rule codes are restored and a fresh upload is required.
4. Upload `demo/messy_students.tsv`, validate, detect structure, and analyze quality.
5. Show restored rules preselected and editable.

## 10. Create And Apply Template

1. Save the current selected rules as a template.
2. Load `Templates`.
3. Open template detail and edit name, description, or rules.
4. Click `Apply Template`.
5. Explain that templates store reusable rule sets only.
6. Clear applied template state or delete the template to finish the demo.

## Closing Line

DataPulse is a deterministic data preparation studio for local CSV and Excel cleaning workflows. It is not AI cleaning, does not store original uploaded files, and keeps transformations transparent through previews, exports, reports, history, and templates.
