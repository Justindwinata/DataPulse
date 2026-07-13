import { ChangeEvent, FormEvent, useState } from "react";

import {
  UploadValidationError,
  validateUploadFile,
  type FileUploadValidationResponse,
} from "./api/uploadValidation";
import {
  StructureDetectionError,
  detectFileStructure,
  type StructureDetectionResult,
} from "./api/structureDetection";
import {
  DataQualityError,
  detectDataQuality,
  type DataQualityIssue,
  type DataQualityResult,
  type IssueSeverity,
} from "./api/dataQuality";

type ProductSection = {
  title: string;
  description: string;
};

const productSections: ProductSection[] = [
  {
    title: "Messy File Upload",
    description: "A planned intake flow for CSV, TSV, text tables, and Excel workbooks.",
  },
  {
    title: "Structure Detection",
    description: "Future profiling will identify headers, sheets, delimiters, and table shape.",
  },
  {
    title: "Rule-Based Cleaning",
    description: "Users will choose transparent deterministic rules before data is changed.",
  },
  {
    title: "Cleaned CSV Export",
    description: "Exports will focus on analysis-ready CSV output instead of spreadsheet styling.",
  },
  {
    title: "Cleaning Reports",
    description: "Reports will document validations, detected issues, and applied transformations.",
  },
];

const acceptedFormats = ".csv,.tsv,.txt,.xlsx,.xls";
const csvLikeExtensions = new Set(["csv", "tsv", "txt"]);
const excelExtensions = new Set(["xlsx", "xls"]);
const issueSeverityOrder: IssueSeverity[] = ["critical", "warning", "info"];

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function uniqueAffectedColumns(issues: DataQualityIssue[]): string[] {
  return Array.from(new Set(issues.flatMap((issue) => issue.affected_columns)));
}

function issuesBySeverity(
  issues: DataQualityIssue[],
  severity: IssueSeverity,
): DataQualityIssue[] {
  return issues.filter((issue) => issue.severity === severity);
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] =
    useState<FileUploadValidationResponse | null>(null);
  const [structureResult, setStructureResult] = useState<StructureDetectionResult | null>(null);
  const [qualityResult, setQualityResult] = useState<DataQualityResult | null>(null);
  const [selectedSheetName, setSelectedSheetName] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [structureErrorMessage, setStructureErrorMessage] = useState<string | null>(null);
  const [qualityErrorMessage, setQualityErrorMessage] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isDetectingStructure, setIsDetectingStructure] = useState(false);
  const [isAnalyzingQuality, setIsAnalyzingQuality] = useState(false);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setValidationResult(null);
    setStructureResult(null);
    setQualityResult(null);
    setSelectedSheetName("");
    setErrorMessage(null);
    setStructureErrorMessage(null);
    setQualityErrorMessage(null);
  };

  const handleValidate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) {
      setErrorMessage("Select a CSV, TSV, TXT, XLSX, or XLS file before validation.");
      return;
    }

    setIsValidating(true);
    setErrorMessage(null);
    setStructureErrorMessage(null);
    setValidationResult(null);
    setStructureResult(null);
    setQualityResult(null);
    setSelectedSheetName("");

    try {
      setValidationResult(await validateUploadFile(selectedFile));
    } catch (error) {
      setErrorMessage(
        error instanceof UploadValidationError
          ? error.message
          : "Upload validation failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsValidating(false);
    }
  };

  const handleDetectStructure = async () => {
    if (!selectedFile) {
      setStructureErrorMessage("Select a file before structure detection.");
      return;
    }

    setIsDetectingStructure(true);
    setStructureErrorMessage(null);
    setQualityErrorMessage(null);
    setStructureResult(null);
    setQualityResult(null);

    try {
      const result = await detectFileStructure(selectedFile);
      setStructureResult(result);
      if (result.workbook?.default_sheet_name) {
        setSelectedSheetName(result.workbook.default_sheet_name);
      }
    } catch (error) {
      setStructureErrorMessage(
        error instanceof StructureDetectionError
          ? error.message
          : "Structure detection failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsDetectingStructure(false);
    }
  };

  const handlePreviewSelectedSheet = async () => {
    if (!selectedFile || !selectedSheetName) {
      setStructureErrorMessage("Choose a sheet before preview.");
      return;
    }

    setIsDetectingStructure(true);
    setStructureErrorMessage(null);
    setQualityErrorMessage(null);
    setQualityResult(null);

    try {
      setStructureResult(await detectFileStructure(selectedFile, selectedSheetName));
    } catch (error) {
      setStructureErrorMessage(
        error instanceof StructureDetectionError
          ? error.message
          : "Structure detection failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsDetectingStructure(false);
    }
  };

  const handleAnalyzeQuality = async () => {
    if (!selectedFile || !structureResult || structureResult.structure_status !== "detected") {
      setQualityErrorMessage("Detect file structure before analyzing data quality.");
      return;
    }

    const sheetName = excelExtensions.has(structureResult.detected_extension)
      ? structureResult.selected_sheet_name ?? selectedSheetName
      : undefined;

    setIsAnalyzingQuality(true);
    setQualityErrorMessage(null);
    setQualityResult(null);

    try {
      setQualityResult(await detectDataQuality(selectedFile, sheetName || undefined));
    } catch (error) {
      setQualityErrorMessage(
        error instanceof DataQualityError
          ? error.message
          : "Data quality analysis failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsAnalyzingQuality(false);
    }
  };

  const canDetectStructure =
    validationResult?.validation_status === "accepted" &&
    (csvLikeExtensions.has(validationResult.detected_extension) ||
      excelExtensions.has(validationResult.detected_extension));
  const isExcelUpload =
    validationResult?.validation_status === "accepted" &&
    ["xlsx", "xls"].includes(validationResult.detected_extension);
  const affectedColumns = qualityResult ? uniqueAffectedColumns(qualityResult.issues) : [];

  return (
    <main className="app-shell">
      <section className="hero" aria-labelledby="product-title">
        <div className="hero-copy">
          <p className="eyebrow">Excel and CSV structure detection</p>
          <h1 id="product-title">DataPulse</h1>
          <p className="subtitle">Messy CSV & Excel Cleaner Studio</p>
          <p className="description">
            Upload a CSV-like or Excel file, validate it, detect table structure,
            then inspect a bounded raw preview. Cleaning, export, and reports remain
            planned for later milestones.
          </p>
        </div>
        <div className="status-panel" aria-label="Current foundation status">
          <span className="status-label">DP-0004</span>
          <strong>Excel sheet preview active</strong>
          <p>CSV-like files and Excel sheets can be previewed as raw values.</p>
        </div>
      </section>

      <section className="upload-workspace" aria-labelledby="upload-title">
        <div className="section-heading">
          <p className="eyebrow">Detection workspace</p>
          <h2 id="upload-title">Validate a file and inspect its raw structure</h2>
        </div>

        <div className="workspace-grid">
          <form className="upload-panel" onSubmit={handleValidate}>
            <label className="drop-zone" htmlFor="file-upload">
              <span className="drop-zone-title">Choose a tabular file</span>
              <span className="drop-zone-copy">
                Drop-style intake for CSV, TSV, TXT, XLSX, and XLS files up to 10 MB.
              </span>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                accept={acceptedFormats}
                onChange={handleFileChange}
              />
            </label>

            <div className="selected-file" aria-live="polite">
              {selectedFile ? (
                <>
                  <div>
                    <span className="meta-label">Selected file</span>
                    <strong>{selectedFile.name}</strong>
                  </div>
                  <dl>
                    <div>
                      <dt>Type</dt>
                      <dd>{selectedFile.type || "Unknown"}</dd>
                    </div>
                    <div>
                      <dt>Size</dt>
                      <dd>{formatFileSize(selectedFile.size)}</dd>
                    </div>
                  </dl>
                </>
              ) : (
                <p>No file selected yet.</p>
              )}
            </div>

            <button className="primary-action" type="submit" disabled={isValidating}>
              {isValidating ? "Validating..." : "Validate upload"}
            </button>
          </form>

          <aside className="result-panel" aria-live="polite" aria-label="Validation result">
            {!validationResult && !errorMessage && (
              <div className="empty-state">
                <span className="status-label">Waiting</span>
                <h3>Validation result will appear here</h3>
                <p>
                  DataPulse checks extension, size, and upload metadata. It does not parse
                  rows until structure detection is requested. It does not clean data,
                  export CSV files, or generate reports in this milestone.
                </p>
              </div>
            )}

            {errorMessage && (
              <div className="result-card rejected">
                <span className="status-label">Error</span>
                <h3>Validation request failed</h3>
                <p>{errorMessage}</p>
              </div>
            )}

            {validationResult && (
              <div
                className={`result-card ${
                  validationResult.validation_status === "accepted" ? "accepted" : "rejected"
                }`}
              >
                <span className="status-label">
                  {validationResult.validation_status === "accepted" ? "Accepted" : "Rejected"}
                </span>
                <h3>{validationResult.safe_filename}</h3>
                <dl className="result-metadata">
                  <div>
                    <dt>Extension</dt>
                    <dd>{validationResult.detected_extension}</dd>
                  </div>
                  <div>
                    <dt>Size</dt>
                    <dd>{formatFileSize(validationResult.file_size_bytes)}</dd>
                  </div>
                  <div>
                    <dt>Next step</dt>
                    <dd>{validationResult.next_step}</dd>
                  </div>
                </dl>
                <ul>
                  {validationResult.validation_messages.map((message) => (
                    <li key={message}>{message}</li>
                  ))}
                </ul>
                <p className="future-note">
                  Structure detection available:{" "}
                  {canDetectStructure ? "yes for this file" : "not for this file yet"}.
                  Cleaning, exports, reports, and saved history come later.
                </p>
                {canDetectStructure && (
                  <button
                    className="secondary-action"
                    type="button"
                    disabled={isDetectingStructure}
                    onClick={handleDetectStructure}
                  >
                    {isDetectingStructure ? "Detecting structure..." : "Detect Structure"}
                  </button>
                )}
                {isExcelUpload && (
                  <p className="excel-note">
                    Excel workbook detected. Preview values only; formatting and formulas are not preserved.
                  </p>
                )}
              </div>
            )}
          </aside>
        </div>
      </section>

      <section className="structure-workspace" aria-labelledby="structure-title">
        <div className="section-heading">
          <p className="eyebrow">Raw preview</p>
          <h2 id="structure-title">Detected structure result</h2>
        </div>

        {!structureResult && !structureErrorMessage && (
          <div className="structure-empty">
            <h3>No structure result yet</h3>
            <p>
              Validate a CSV, TSV, TXT, XLSX, or XLS file, then run structure detection
              to see sheets, headers, warnings, and a bounded preview.
            </p>
          </div>
        )}

        {structureErrorMessage && (
          <div className="result-card rejected">
            <span className="status-label">Error</span>
            <h3>Structure detection request failed</h3>
            <p>{structureErrorMessage}</p>
          </div>
        )}

        {structureResult && structureResult.structure_status === "sheet_selection_required" && (
          <div className="structure-result">
            <span className="status-label">Excel workbook detected</span>
            <h3>Choose a sheet to preview</h3>
            <p className="workbook-copy">
              Preview values only; formatting and formulas are not preserved.
            </p>
            <div className="sheet-selector">
              <label htmlFor="sheet-selector">Sheet</label>
              <select
                id="sheet-selector"
                value={selectedSheetName}
                onChange={(event) => setSelectedSheetName(event.target.value)}
              >
                {structureResult.workbook?.sheet_names.map((sheetName) => (
                  <option key={sheetName} value={sheetName}>
                    {sheetName}
                  </option>
                ))}
              </select>
              <button
                className="secondary-action"
                type="button"
                disabled={isDetectingStructure || !selectedSheetName}
                onClick={handlePreviewSelectedSheet}
              >
                {isDetectingStructure ? "Previewing sheet..." : "Preview selected sheet"}
              </button>
            </div>
            <div className="sheet-list">
              {structureResult.workbook?.sheets.map((sheet) => (
                <article key={sheet.sheet_name}>
                  <strong>{sheet.sheet_name}</strong>
                  <span>
                    {sheet.max_row ?? 0} rows x {sheet.max_column ?? 0} columns
                  </span>
                </article>
              ))}
            </div>
            {structureResult.warnings.length > 0 && (
              <div className="warning-panel">
                <h3>Excel limitations</h3>
                <ul>
                  {structureResult.warnings.map((warning) => (
                    <li key={warning.code}>
                      <strong>{warning.code}</strong>
                      <span>{warning.message}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {structureResult &&
          structureResult.structure_status !== "detected" &&
          structureResult.structure_status !== "sheet_selection_required" && (
          <div className="result-card rejected">
            <span className="status-label">
              {structureResult.structure_status === "not_implemented" ? "Planned" : "Rejected"}
            </span>
            <h3>{structureResult.safe_filename}</h3>
            {structureResult.warnings.map((warning) => (
              <p key={warning.code}>{warning.message}</p>
            ))}
          </div>
        )}

        {structureResult && structureResult.structure_status === "detected" && (
          <div className="structure-result">
            <div className="summary-grid">
              <article>
                <span>{structureResult.selected_sheet_name ? "Sheet" : "Delimiter"}</span>
                <strong>
                  {structureResult.selected_sheet_name ??
                    structureResult.delimiter?.delimiter_label ??
                    "unknown"}
                </strong>
                <p>
                  {structureResult.selected_sheet_name
                    ? "Selected worksheet"
                    : `${structureResult.delimiter?.delimiter_confidence ?? "unknown"} confidence`}
                </p>
              </article>
              <article>
                <span>Columns</span>
                <strong>{structureResult.detected_column_count}</strong>
                <p>{structureResult.has_detected_header ? "Header detected" : "Generated names"}</p>
              </article>
              <article>
                <span>Preview rows</span>
                <strong>{structureResult.preview_row_count}</strong>
                <p>{structureResult.sampled_row_count} sampled rows</p>
              </article>
              <article>
                <span>Warnings</span>
                <strong>{structureResult.warnings.length}</strong>
                <p>Structure notes found</p>
              </article>
            </div>

            {structureResult.warnings.length > 0 && (
              <div className="warning-panel">
                <h3>Structure warnings</h3>
                <ul>
                  {structureResult.warnings.map((warning) => (
                    <li key={warning.code}>
                      <strong>{warning.code}</strong>
                      <span>{warning.message}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {structureResult.preview && (
              <div className="preview-panel">
                <div className="preview-heading">
                  <h3>Raw preview</h3>
                  <p>Preview rows are bounded and normalized for display only.</p>
                </div>
                <div className="table-scroll" role="region" aria-label="Raw preview table">
                  <table>
                    <thead>
                      <tr>
                        {structureResult.preview.columns.map((column) => (
                          <th key={column}>{column}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {structureResult.preview.rows.map((row, rowIndex) => (
                        <tr key={`${row.join("|")}-${rowIndex}`}>
                          {row.map((cell, cellIndex) => (
                            <td key={`${cellIndex}-${cell}`}>{cell}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <p className="future-note">
              Next: analyze data quality before cleaning rules are implemented.
            </p>
            <button
              className="secondary-action"
              type="button"
              disabled={isAnalyzingQuality}
              onClick={handleAnalyzeQuality}
            >
              {isAnalyzingQuality ? "Analyzing data quality..." : "Analyze Data Quality"}
            </button>
          </div>
        )}
      </section>

      <section className="quality-workspace" aria-labelledby="quality-title">
        <div className="section-heading">
          <p className="eyebrow">Data quality</p>
          <h2 id="quality-title">Issue summary and column profile</h2>
        </div>

        {!qualityResult && !qualityErrorMessage && (
          <div className="quality-empty">
            <h3>No quality profile yet</h3>
            <p>
              Run structure detection first, then analyze the bounded sample for missing
              values, duplicate rows, type patterns, whitespace, and column-level issues.
            </p>
          </div>
        )}

        {qualityErrorMessage && (
          <div className="result-card rejected">
            <span className="status-label">Error</span>
            <h3>Data quality request failed</h3>
            <p>{qualityErrorMessage}</p>
          </div>
        )}

        {qualityResult && qualityResult.quality_status !== "profiled" && (
          <div className="result-card rejected">
            <span className="status-label">
              {qualityResult.quality_status === "sheet_selection_required"
                ? "Sheet required"
                : "Rejected"}
            </span>
            <h3>{qualityResult.safe_filename}</h3>
            {qualityResult.messages.map((message) => (
              <p key={message}>{message}</p>
            ))}
          </div>
        )}

        {qualityResult && qualityResult.quality_status === "profiled" && (
          <div className="quality-result">
            <div className="summary-grid quality-summary">
              <article>
                <span>Quality score</span>
                <strong>{qualityResult.quality_score}</strong>
                <p>Heuristic sample score</p>
              </article>
              <article>
                <span>Total issues</span>
                <strong>{qualityResult.total_issue_count}</strong>
                <p>{qualityResult.sampled_row_count} sampled rows</p>
              </article>
              <article>
                <span>Warnings</span>
                <strong>{qualityResult.severity_counts.warning}</strong>
                <p>{qualityResult.severity_counts.critical} critical</p>
              </article>
              <article>
                <span>Affected columns</span>
                <strong>{affectedColumns.length}</strong>
                <p>{qualityResult.severity_counts.info} info notes</p>
              </article>
            </div>

            {qualityResult.issues.length > 0 ? (
              <div className="issue-panel">
                <h3>Detected issues</h3>
                {issueSeverityOrder.map((severity) => {
                  const groupedIssues = issuesBySeverity(qualityResult.issues, severity);
                  if (groupedIssues.length === 0) {
                    return null;
                  }
                  return (
                    <div className="issue-group" key={severity}>
                      <h4>{severity}</h4>
                      <div className="issue-card-grid">
                        {groupedIssues.map((issue) => (
                          <article className={`issue-card ${issue.severity}`} key={issue.code}>
                            <span>{issue.code}</span>
                            <h5>{issue.title}</h5>
                            <p>{issue.message}</p>
                            {issue.affected_columns.length > 0 && (
                              <p>
                                <strong>Columns:</strong> {issue.affected_columns.join(", ")}
                              </p>
                            )}
                            {issue.affected_row_count !== null && (
                              <p>
                                <strong>Rows:</strong> {issue.affected_row_count}
                              </p>
                            )}
                            {issue.suggested_cleaning_rule && (
                              <p>
                                <strong>Future rule:</strong> {issue.suggested_cleaning_rule}
                              </p>
                            )}
                          </article>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="issue-panel">
                <h3>No issues detected in the sampled data</h3>
                <p>The profile is sample-based and does not guarantee the full file is clean.</p>
              </div>
            )}

            <div className="preview-panel">
              <div className="preview-heading">
                <h3>Column profile</h3>
                <p>Types and counts are inferred from the bounded sample.</p>
              </div>
              <div className="table-scroll" role="region" aria-label="Column profile table">
                <table>
                  <thead>
                    <tr>
                      <th>Column</th>
                      <th>Type</th>
                      <th>Missing</th>
                      <th>Missing %</th>
                      <th>Unique</th>
                      <th>Issues</th>
                    </tr>
                  </thead>
                  <tbody>
                    {qualityResult.columns.map((column) => (
                      <tr key={`${column.column_index}-${column.column_name}`}>
                        <td>{column.column_name}</td>
                        <td>{column.inferred_type}</td>
                        <td>{column.missing_count}</td>
                        <td>{column.missing_percentage}%</td>
                        <td>{column.unique_count}</td>
                        <td>
                          {column.issues.length > 0 ? (
                            <span className="issue-badges">{column.issues.join(", ")}</span>
                          ) : (
                            "None"
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <p className="future-note">
              Cleaning rules will be available in the next milestone. DataPulse has not
              modified your file yet.
            </p>
          </div>
        )}
      </section>

      <section className="workflow" aria-labelledby="workflow-title">
        <div className="section-heading">
          <p className="eyebrow">Future workflow</p>
          <h2 id="workflow-title">From messy table to documented CSV</h2>
        </div>
        <div className="feature-grid">
          {productSections.map((section) => (
            <article className="feature-card" key={section.title}>
              <h3>{section.title}</h3>
              <p>{section.description}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
