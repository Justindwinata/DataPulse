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
import {
  CleaningPreviewError,
  generateCleaningPreview,
  type CleaningPreviewResult,
  type CleaningRuleCode,
} from "./api/cleaningPreview";
import {
  CleanedCsvExportError,
  exportCleanedCsv,
} from "./api/cleanedCsvExport";
import {
  CleaningReportError,
  generateCleaningReport,
} from "./api/cleaningReport";
import {
  SavedSessionsError,
  createSession,
  deleteSession,
  generateSavedSessionReport,
  getSession,
  listSessions,
  type SavedCleaningSessionDetail,
  type SavedCleaningSessionSummary,
  type SavedCleaningSessionCreate,
} from "./api/savedSessions";

type ProductSection = {
  title: string;
  description: string;
};

const productSections: ProductSection[] = [
  {
    title: "Messy File Upload",
    description: "Validate CSV, TSV, text tables, and Excel workbooks before inspection.",
  },
  {
    title: "Structure Detection",
    description: "Identify headers, sheets, delimiters, warnings, and table shape.",
  },
  {
    title: "Rule-Based Cleaning",
    description: "Choose transparent deterministic rules and inspect the cleaned preview.",
  },
  {
    title: "Cleaned CSV Export",
    description: "Download analysis-ready CSV output instead of spreadsheet styling.",
  },
  {
    title: "Cleaning Reports",
    description: "Open live HTML reports and replay saved reports from local history.",
  },
];

const acceptedFormats = ".csv,.tsv,.txt,.xlsx,.xls";
const csvLikeExtensions = new Set(["csv", "tsv", "txt"]);
const excelExtensions = new Set(["xlsx", "xls"]);
const issueSeverityOrder: IssueSeverity[] = ["critical", "warning", "info"];
const cleaningRules: Array<{
  code: CleaningRuleCode;
  label: string;
  description: string;
  issueCodes: string[];
}> = [
  {
    code: "trim_whitespace",
    label: "Trim whitespace",
    description: "Remove leading and trailing spaces from sampled text cells.",
    issueCodes: ["leading_trailing_whitespace"],
  },
  {
    code: "remove_empty_rows",
    label: "Remove empty rows",
    description: "Remove rows where every sampled cell is empty.",
    issueCodes: ["empty_rows"],
  },
  {
    code: "remove_duplicate_rows",
    label: "Remove duplicate rows",
    description: "Keep the first exact row and remove repeated sampled rows.",
    issueCodes: ["duplicate_rows"],
  },
  {
    code: "drop_empty_columns",
    label: "Drop empty columns",
    description: "Remove columns with no values in the sampled rows.",
    issueCodes: ["empty_columns"],
  },
  {
    code: "standardize_column_names",
    label: "Standardize column names",
    description: "Convert column names to lowercase snake_case.",
    issueCodes: ["messy_column_names", "duplicate_column_names"],
  },
  {
    code: "generate_missing_column_names",
    label: "Generate missing column names",
    description: "Fill missing headers with generated column names.",
    issueCodes: ["missing_column_names"],
  },
];

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

function buildSessionPayload(
  validationResult: FileUploadValidationResponse,
  structureResult: StructureDetectionResult,
  qualityResult: DataQualityResult,
  cleaningResult: CleaningPreviewResult,
  selectedRules: CleaningRuleCode[],
): SavedCleaningSessionCreate {
  return {
    source_filename: validationResult.safe_filename,
    detected_extension: validationResult.detected_extension,
    content_type: validationResult.content_type,
    file_size_bytes: validationResult.file_size_bytes,
    selected_sheet_name: cleaningResult.selected_sheet_name,
    structure_summary: {
      structure_status: structureResult.structure_status,
      detected_column_count: structureResult.detected_column_count,
      sampled_row_count: structureResult.sampled_row_count,
      preview_row_count: structureResult.preview_row_count,
      has_detected_header: structureResult.has_detected_header,
      header_row_index: structureResult.header_row_index,
      delimiter_label: structureResult.delimiter?.delimiter_label ?? null,
      selected_sheet_name: structureResult.selected_sheet_name,
      warnings: structureResult.warnings,
      column_names: structureResult.column_names,
    },
    quality_summary: {
      quality_score: qualityResult.quality_score,
      total_issue_count: qualityResult.total_issue_count,
      severity_counts: qualityResult.severity_counts,
      sampled_row_count: qualityResult.sampled_row_count,
      detected_column_count: qualityResult.detected_column_count,
      issues: qualityResult.issues,
    },
    selected_rules: selectedRules,
    cleaning_summary: {
      before_summary: cleaningResult.before_summary,
      after_summary: cleaningResult.after_summary,
      warnings: cleaningResult.warnings,
    },
    rule_effects: cleaningResult.rule_effects,
    export_summary: {
      format: "CSV",
      csv_first_strategy: true,
      original_file_modified: false,
    },
    report_summary: {
      format: "HTML",
      generated_from_metadata: true,
    },
    preview_snapshot: cleaningResult.cleaned_preview,
  };
}

function numberOrDash(value: number | null | undefined): string {
  return value === null || value === undefined ? "-" : String(value);
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString();
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] =
    useState<FileUploadValidationResponse | null>(null);
  const [structureResult, setStructureResult] = useState<StructureDetectionResult | null>(null);
  const [qualityResult, setQualityResult] = useState<DataQualityResult | null>(null);
  const [cleaningResult, setCleaningResult] = useState<CleaningPreviewResult | null>(null);
  const [selectedRules, setSelectedRules] = useState<CleaningRuleCode[]>([]);
  const [selectedSheetName, setSelectedSheetName] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [structureErrorMessage, setStructureErrorMessage] = useState<string | null>(null);
  const [qualityErrorMessage, setQualityErrorMessage] = useState<string | null>(null);
  const [cleaningErrorMessage, setCleaningErrorMessage] = useState<string | null>(null);
  const [exportErrorMessage, setExportErrorMessage] = useState<string | null>(null);
  const [exportSuccessMessage, setExportSuccessMessage] = useState<string | null>(null);
  const [reportErrorMessage, setReportErrorMessage] = useState<string | null>(null);
  const [reportSuccessMessage, setReportSuccessMessage] = useState<string | null>(null);
  const [saveSessionErrorMessage, setSaveSessionErrorMessage] = useState<string | null>(null);
  const [saveSessionSuccessMessage, setSaveSessionSuccessMessage] = useState<string | null>(null);
  const [historyErrorMessage, setHistoryErrorMessage] = useState<string | null>(null);
  const [historySuccessMessage, setHistorySuccessMessage] = useState<string | null>(null);
  const [savedReportErrorMessage, setSavedReportErrorMessage] = useState<string | null>(null);
  const [savedReportSuccessMessage, setSavedReportSuccessMessage] = useState<string | null>(null);
  const [savedSessions, setSavedSessions] = useState<SavedCleaningSessionSummary[]>([]);
  const [selectedSavedSession, setSelectedSavedSession] =
    useState<SavedCleaningSessionDetail | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isDetectingStructure, setIsDetectingStructure] = useState(false);
  const [isAnalyzingQuality, setIsAnalyzingQuality] = useState(false);
  const [isGeneratingCleaningPreview, setIsGeneratingCleaningPreview] = useState(false);
  const [isExportingCsv, setIsExportingCsv] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isSavingSession, setIsSavingSession] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isDeletingSessionId, setIsDeletingSessionId] = useState<number | null>(null);
  const [isGeneratingSavedReport, setIsGeneratingSavedReport] = useState(false);

  const clearReportStatus = () => {
    setReportErrorMessage(null);
    setReportSuccessMessage(null);
  };

  const clearSaveSessionStatus = () => {
    setSaveSessionErrorMessage(null);
    setSaveSessionSuccessMessage(null);
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setValidationResult(null);
    setStructureResult(null);
    setQualityResult(null);
    setCleaningResult(null);
    setSelectedRules([]);
    setSelectedSheetName("");
    setErrorMessage(null);
    setStructureErrorMessage(null);
    setQualityErrorMessage(null);
    setCleaningErrorMessage(null);
    setExportErrorMessage(null);
    setExportSuccessMessage(null);
    clearReportStatus();
    clearSaveSessionStatus();
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
    setCleaningResult(null);
    setSelectedRules([]);
    setExportErrorMessage(null);
    setExportSuccessMessage(null);
    clearReportStatus();
    clearSaveSessionStatus();
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
    setCleaningErrorMessage(null);
    setStructureResult(null);
    setQualityResult(null);
    setCleaningResult(null);
    setSelectedRules([]);
    setExportErrorMessage(null);
    setExportSuccessMessage(null);
    clearReportStatus();
    clearSaveSessionStatus();

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
    setCleaningErrorMessage(null);
    setQualityResult(null);
    setCleaningResult(null);
    setSelectedRules([]);
    setExportErrorMessage(null);
    setExportSuccessMessage(null);
    clearReportStatus();
    clearSaveSessionStatus();

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
    setCleaningErrorMessage(null);
    setQualityResult(null);
    setCleaningResult(null);
    setSelectedRules([]);
    setExportErrorMessage(null);
    setExportSuccessMessage(null);
    clearReportStatus();
    clearSaveSessionStatus();

    try {
      const result = await detectDataQuality(selectedFile, sheetName || undefined);
      setQualityResult(result);
      setSelectedRules(
        cleaningRules
          .filter((rule) =>
            result.issues.some((issue) => rule.issueCodes.includes(issue.code)),
          )
          .map((rule) => rule.code),
      );
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

  const handleRuleToggle = (rule: CleaningRuleCode) => {
    setSelectedRules((currentRules) =>
      currentRules.includes(rule)
        ? currentRules.filter((currentRule) => currentRule !== rule)
        : [...currentRules, rule],
    );
    setCleaningResult(null);
    setCleaningErrorMessage(null);
    setExportErrorMessage(null);
    setExportSuccessMessage(null);
    clearReportStatus();
    clearSaveSessionStatus();
  };

  const handleGenerateCleaningPreview = async () => {
    if (!selectedFile || !qualityResult || qualityResult.quality_status !== "profiled") {
      setCleaningErrorMessage("Analyze data quality before generating a cleaned preview.");
      return;
    }

    const sheetName = excelExtensions.has(qualityResult.detected_extension)
      ? qualityResult.selected_sheet_name ?? selectedSheetName
      : undefined;

    setIsGeneratingCleaningPreview(true);
    setCleaningErrorMessage(null);
    setCleaningResult(null);
    setExportErrorMessage(null);
    setExportSuccessMessage(null);
    clearReportStatus();
    clearSaveSessionStatus();

    try {
      setCleaningResult(
        await generateCleaningPreview(selectedFile, selectedRules, sheetName || undefined),
      );
    } catch (error) {
      setCleaningErrorMessage(
        error instanceof CleaningPreviewError
          ? error.message
          : "Cleaning preview failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsGeneratingCleaningPreview(false);
    }
  };

  const handleSaveCleaningSession = async () => {
    if (
      !validationResult ||
      !structureResult ||
      !qualityResult ||
      !cleaningResult ||
      cleaningResult.cleaning_status !== "preview_generated"
    ) {
      setSaveSessionErrorMessage("Generate a cleaned preview before saving a session.");
      return;
    }

    setIsSavingSession(true);
    setSaveSessionErrorMessage(null);
    setSaveSessionSuccessMessage(null);

    try {
      const saved = await createSession(
        buildSessionPayload(
          validationResult,
          structureResult,
          qualityResult,
          cleaningResult,
          selectedRules,
        ),
      );
      setSaveSessionSuccessMessage(`Saved session #${saved.id} locally.`);
      setSavedSessions((currentSessions) => [saved, ...currentSessions]);
      setSelectedSavedSession(saved);
      setHistorySuccessMessage("History updated with the latest saved session.");
    } catch (error) {
      setSaveSessionErrorMessage(
        error instanceof SavedSessionsError
          ? error.message
          : "Saving the cleaning session failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsSavingSession(false);
    }
  };

  const handleExportCleanedCsv = async () => {
    if (!selectedFile || !cleaningResult || cleaningResult.cleaning_status !== "preview_generated") {
      setExportErrorMessage("Generate a cleaned preview before downloading CSV.");
      return;
    }

    const sheetName = excelExtensions.has(cleaningResult.detected_extension)
      ? cleaningResult.selected_sheet_name ?? selectedSheetName
      : undefined;

    setIsExportingCsv(true);
    setExportErrorMessage(null);
    setExportSuccessMessage(null);

    try {
      const download = await exportCleanedCsv(selectedFile, selectedRules, sheetName || undefined);
      const url = URL.createObjectURL(download.blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = download.filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setExportSuccessMessage(`Downloaded ${download.filename}`);
    } catch (error) {
      setExportErrorMessage(
        error instanceof CleanedCsvExportError
          ? error.message
          : "Cleaned CSV export failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsExportingCsv(false);
    }
  };

  const handleOpenCleaningReport = async () => {
    if (!selectedFile || !cleaningResult || cleaningResult.cleaning_status !== "preview_generated") {
      setReportErrorMessage("Generate a cleaned preview before opening an HTML report.");
      return;
    }

    const sheetName = excelExtensions.has(cleaningResult.detected_extension)
      ? cleaningResult.selected_sheet_name ?? selectedSheetName
      : undefined;

    setIsGeneratingReport(true);
    setReportErrorMessage(null);
    setReportSuccessMessage(null);

    try {
      const blob = await generateCleaningReport(selectedFile, selectedRules, sheetName || undefined);
      const url = URL.createObjectURL(blob);
      const openedWindow = window.open(url, "_blank", "noopener,noreferrer");
      setReportSuccessMessage(
        openedWindow
          ? "Opened HTML cleaning report."
          : "Generated HTML cleaning report. Allow pop-ups if the report did not open.",
      );
    } catch (error) {
      setReportErrorMessage(
        error instanceof CleaningReportError
          ? error.message
          : "HTML cleaning report generation failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const handleLoadHistory = async () => {
    setIsLoadingHistory(true);
    setHistoryErrorMessage(null);
    setHistorySuccessMessage(null);

    try {
      const response = await listSessions();
      setSavedSessions(response.sessions);
      if (response.sessions.length === 0) {
        setSelectedSavedSession(null);
      }
    } catch (error) {
      setHistoryErrorMessage(
        error instanceof SavedSessionsError
          ? error.message
          : "Loading saved sessions failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleOpenSessionDetail = async (sessionId: number) => {
    setHistoryErrorMessage(null);
    setHistorySuccessMessage(null);
    setSavedReportErrorMessage(null);
    setSavedReportSuccessMessage(null);

    try {
      setSelectedSavedSession(await getSession(sessionId));
    } catch (error) {
      setHistoryErrorMessage(
        error instanceof SavedSessionsError
          ? error.message
          : "Loading saved session detail failed. Confirm the backend is running and try again.",
      );
    }
  };

  const handleOpenSavedSessionReport = async () => {
    if (!selectedSavedSession) {
      setSavedReportErrorMessage("Open a saved session detail before generating a saved report.");
      return;
    }

    setIsGeneratingSavedReport(true);
    setSavedReportErrorMessage(null);
    setSavedReportSuccessMessage(null);

    try {
      const blob = await generateSavedSessionReport(selectedSavedSession.id);
      const url = URL.createObjectURL(blob);
      const openedWindow = window.open(url, "_blank", "noopener,noreferrer");
      setSavedReportSuccessMessage(
        openedWindow
          ? "Opened saved HTML report."
          : "Generated saved HTML report. Allow pop-ups if the report did not open.",
      );
    } catch (error) {
      setSavedReportErrorMessage(
        error instanceof SavedSessionsError
          ? error.message
          : "Saved HTML report generation failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsGeneratingSavedReport(false);
    }
  };

  const handleDeleteSession = async (sessionId: number) => {
    if (!window.confirm("Delete this saved cleaning session? Original uploaded files are not stored.")) {
      return;
    }

    setIsDeletingSessionId(sessionId);
    setHistoryErrorMessage(null);
    setHistorySuccessMessage(null);

    try {
      await deleteSession(sessionId);
      setSavedSessions((currentSessions) =>
        currentSessions.filter((session) => session.id !== sessionId),
      );
      if (selectedSavedSession?.id === sessionId) {
        setSelectedSavedSession(null);
      }
      setHistorySuccessMessage(`Deleted saved session #${sessionId}.`);
    } catch (error) {
      setHistoryErrorMessage(
        error instanceof SavedSessionsError
          ? error.message
          : "Deleting saved session failed. Confirm the backend is running and try again.",
      );
    } finally {
      setIsDeletingSessionId(null);
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
  const detectedIssueCodes = new Set(qualityResult?.issues.map((issue) => issue.code) ?? []);

  return (
    <main className="app-shell">
      <section className="hero" aria-labelledby="product-title">
        <div className="hero-copy">
          <p className="eyebrow">CSV and Excel cleaning reports</p>
          <h1 id="product-title">DataPulse</h1>
          <p className="subtitle">Messy CSV & Excel Cleaner Studio</p>
          <p className="description">
            Upload a CSV-like or Excel file, validate it, detect structure,
            analyze quality issues, apply deterministic cleaning rules, export CSV,
            open standalone HTML reports, and replay saved reports from local history.
          </p>
        </div>
        <div className="status-panel" aria-label="Current foundation status">
          <span className="status-label">DP-0010</span>
          <strong>Saved report replay active</strong>
          <p>Saved cleaning sessions can open metadata-based HTML reports without re-uploading files.</p>
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
                  Cleaning, exports, reports, and saved history unlock as the workflow progresses.
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
              Select cleaning rules below to generate a sample-based cleaned preview.
              DataPulse has not modified your file yet.
            </p>
          </div>
        )}
      </section>

      {qualityResult && qualityResult.quality_status === "profiled" && (
        <section className="cleaning-workspace" aria-labelledby="cleaning-title">
          <div className="section-heading">
            <p className="eyebrow">Cleaning rules</p>
            <h2 id="cleaning-title">Select rules and preview cleaned data</h2>
          </div>

          <div className="cleaning-result">
            <div className="rule-grid" aria-label="Cleaning rule selection">
              {cleaningRules.map((rule) => {
                const isRecommended = rule.issueCodes.some((issueCode) =>
                  detectedIssueCodes.has(issueCode),
                );
                return (
                  <label className="rule-card" key={rule.code}>
                    <input
                      type="checkbox"
                      checked={selectedRules.includes(rule.code)}
                      onChange={() => handleRuleToggle(rule.code)}
                    />
                    <span>
                      <strong>{rule.label}</strong>
                      {isRecommended && <em>Recommended</em>}
                    </span>
                    <p>{rule.description}</p>
                  </label>
                );
              })}
            </div>

            <button
              className="secondary-action"
              type="button"
              disabled={isGeneratingCleaningPreview}
              onClick={handleGenerateCleaningPreview}
            >
              {isGeneratingCleaningPreview
                ? "Generating cleaned preview..."
                : "Generate Cleaned Preview"}
            </button>

            {cleaningErrorMessage && (
              <div className="result-card rejected compact-result">
                <span className="status-label">Error</span>
                <h3>Cleaning preview request failed</h3>
                <p>{cleaningErrorMessage}</p>
              </div>
            )}

            {cleaningResult && cleaningResult.cleaning_status !== "preview_generated" && (
              <div className="result-card rejected compact-result">
                <span className="status-label">
                  {cleaningResult.cleaning_status === "sheet_selection_required"
                    ? "Sheet required"
                    : "Rejected"}
                </span>
                <h3>{cleaningResult.safe_filename}</h3>
                {cleaningResult.warnings.map((warning) => (
                  <p key={warning.code}>{warning.message}</p>
                ))}
              </div>
            )}

            {cleaningResult && cleaningResult.cleaning_status === "preview_generated" && (
              <div className="cleaned-preview">
                <div className="summary-grid">
                  <article>
                    <span>Rows before</span>
                    <strong>{cleaningResult.before_summary.row_count}</strong>
                    <p>{cleaningResult.before_summary.empty_rows_count} empty rows</p>
                  </article>
                  <article>
                    <span>Rows after</span>
                    <strong>{cleaningResult.after_summary.row_count}</strong>
                    <p>{cleaningResult.after_summary.removed_empty_rows_count} removed</p>
                  </article>
                  <article>
                    <span>Columns before</span>
                    <strong>{cleaningResult.before_summary.column_count}</strong>
                    <p>{cleaningResult.before_summary.empty_columns_count} empty columns</p>
                  </article>
                  <article>
                    <span>Columns after</span>
                    <strong>{cleaningResult.after_summary.column_count}</strong>
                    <p>{cleaningResult.after_summary.dropped_empty_columns_count} dropped</p>
                  </article>
                </div>

                <div className="summary-grid compact-summary">
                  <article>
                    <span>Duplicates</span>
                    <strong>{cleaningResult.after_summary.removed_duplicate_rows_count}</strong>
                    <p>removed rows</p>
                  </article>
                  <article>
                    <span>Renamed</span>
                    <strong>{cleaningResult.after_summary.renamed_columns_count}</strong>
                    <p>columns changed</p>
                  </article>
                </div>

                {cleaningResult.warnings.length > 0 && (
                  <div className="warning-panel">
                    <h3>Cleaning preview notes</h3>
                    <ul>
                      {cleaningResult.warnings.map((warning) => (
                        <li key={warning.code}>
                          <strong>{warning.code}</strong>
                          <span>{warning.message}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="issue-panel">
                  <h3>Rule effects</h3>
                  <div className="issue-card-grid">
                    {cleaningResult.rule_effects.map((effect) => (
                      <article className={`issue-card ${effect.status}`} key={effect.rule}>
                        <span>{effect.status}</span>
                        <h5>{effect.label}</h5>
                        <p>{effect.message}</p>
                        <p>
                          <strong>Rows:</strong> {effect.affected_rows}
                        </p>
                        <p>
                          <strong>Columns:</strong> {effect.affected_columns}
                        </p>
                      </article>
                    ))}
                  </div>
                </div>

                <div className="preview-panel">
                  <div className="preview-heading">
                    <h3>Cleaned preview</h3>
                    <p>Preview rows are sample-based and capped at 20.</p>
                  </div>
                  <div className="table-scroll" role="region" aria-label="Cleaned preview table">
                    <table>
                      <thead>
                        <tr>
                          {cleaningResult.cleaned_preview.columns.map((column) => (
                            <th key={column}>{column}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {cleaningResult.cleaned_preview.rows.map((row, rowIndex) => (
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

                <p className="future-note">
                  DataPulse has not modified your original file. Export is CSV-first and
                  generated from your selected deterministic rules.
                </p>

                <div className="export-panel" aria-label="Cleaned CSV export panel">
                  <div>
                    <span className="status-label">CSV export</span>
                    <h3>Download cleaned CSV</h3>
                    <p>
                      {selectedRules.length} selected rules. Source:{" "}
                      {cleaningResult.safe_filename}
                      {cleaningResult.selected_sheet_name
                        ? `, sheet ${cleaningResult.selected_sheet_name}`
                        : ""}
                      .
                    </p>
                    {excelExtensions.has(cleaningResult.detected_extension) && (
                      <p>
                        Excel formatting, formulas, charts, and merged cell behavior are
                        not preserved. DataPulse exports cleaned values as CSV.
                      </p>
                    )}
                  </div>
                  <button
                    className="primary-action"
                    type="button"
                    disabled={isExportingCsv}
                    onClick={handleExportCleanedCsv}
                  >
                    {isExportingCsv ? "Downloading..." : "Download Cleaned CSV"}
                  </button>
                  {exportSuccessMessage && (
                    <p className="export-status success">{exportSuccessMessage}</p>
                  )}
                  {exportErrorMessage && (
                    <p className="export-status error">{exportErrorMessage}</p>
                  )}
                </div>

                <div className="report-panel" aria-label="HTML cleaning report panel">
                  <div>
                    <span className="status-label">HTML report</span>
                    <h3>Open HTML Cleaning Report</h3>
                    <p>
                      Report format: HTML. Includes structure summary, data quality issues,
                      column profiles, selected rules, rule effects, cleaned preview, and CSV export notes.
                    </p>
                    {excelExtensions.has(cleaningResult.detected_extension) && (
                      <p>
                        Excel values are reported only as table values. Formatting, formulas,
                        charts, and merged cell behavior are not preserved.
                      </p>
                    )}
                    <p>Use the saved session panel below to store metadata locally.</p>
                  </div>
                  <button
                    className="primary-action"
                    type="button"
                    disabled={isGeneratingReport}
                    onClick={handleOpenCleaningReport}
                  >
                    {isGeneratingReport ? "Generating report..." : "Open HTML Cleaning Report"}
                  </button>
                  {reportSuccessMessage && (
                    <p className="export-status success">{reportSuccessMessage}</p>
                  )}
                  {reportErrorMessage && (
                    <p className="export-status error">{reportErrorMessage}</p>
                  )}
                </div>

                <div className="save-session-panel" aria-label="Save cleaning session panel">
                  <div>
                    <span className="status-label">Saved locally</span>
                    <h3>Save Cleaning Session</h3>
                    <p>
                      Save workflow metadata, quality summaries, selected rules, rule effects,
                      and a small cleaned preview snapshot. Original uploaded files are not stored.
                    </p>
                    <p>History is local to this backend SQLite database.</p>
                  </div>
                  <button
                    className="primary-action"
                    type="button"
                    disabled={isSavingSession}
                    onClick={handleSaveCleaningSession}
                  >
                    {isSavingSession ? "Saving session..." : "Save Cleaning Session"}
                  </button>
                  {saveSessionSuccessMessage && (
                    <p className="export-status success">{saveSessionSuccessMessage}</p>
                  )}
                  {saveSessionErrorMessage && (
                    <p className="export-status error">{saveSessionErrorMessage}</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      <section className="history-workspace" aria-labelledby="history-title">
        <div className="section-heading">
          <p className="eyebrow">History</p>
          <h2 id="history-title">Saved cleaning sessions</h2>
        </div>

        <div className="history-result">
          <div className="history-header">
            <div>
              <span className="status-label">Saved locally</span>
              <h3>Review local cleaning history</h3>
              <p>
                History stores cleaning summaries and metadata in local SQLite.
                Original uploaded files are not stored.
              </p>
            </div>
            <button
              className="secondary-action"
              type="button"
              disabled={isLoadingHistory}
              onClick={handleLoadHistory}
            >
              {isLoadingHistory ? "Loading history..." : "Load Saved Sessions"}
            </button>
          </div>

          {historySuccessMessage && (
            <p className="export-status success">{historySuccessMessage}</p>
          )}
          {historyErrorMessage && (
            <p className="export-status error">{historyErrorMessage}</p>
          )}

          {savedSessions.length === 0 ? (
            <div className="history-empty">
              <h3>Save a cleaning session to review your data preparation history.</h3>
              <p>Saved history is metadata-first and local to this backend instance.</p>
            </div>
          ) : (
            <div className="history-grid">
              <div className="table-scroll" role="region" aria-label="Saved sessions table">
                <table>
                  <thead>
                    <tr>
                      <th>File</th>
                      <th>Type</th>
                      <th>Sheet</th>
                      <th>Score</th>
                      <th>Rules</th>
                      <th>Rows</th>
                      <th>Columns</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {savedSessions.map((session) => (
                      <tr key={session.id}>
                        <td>{session.source_filename}</td>
                        <td>{session.detected_extension}</td>
                        <td>{session.selected_sheet_name ?? "-"}</td>
                        <td>{numberOrDash(session.quality_score)}</td>
                        <td>{session.selected_rules_count}</td>
                        <td>
                          {numberOrDash(session.rows_before)} {"->"} {numberOrDash(session.rows_after)}
                        </td>
                        <td>
                          {numberOrDash(session.columns_before)} {"->"}{" "}
                          {numberOrDash(session.columns_after)}
                        </td>
                        <td>{formatDateTime(session.created_at)}</td>
                        <td>
                          <div className="history-actions">
                            <button
                              type="button"
                              onClick={() => handleOpenSessionDetail(session.id)}
                            >
                              View Detail
                            </button>
                            <button
                              type="button"
                              disabled={isDeletingSessionId === session.id}
                              onClick={() => handleDeleteSession(session.id)}
                            >
                              {isDeletingSessionId === session.id ? "Deleting..." : "Delete"}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {selectedSavedSession && (
                <article className="session-detail" aria-label="Saved session detail">
                  <h3>{selectedSavedSession.source_filename}</h3>
                  <p>{selectedSavedSession.storage_note}</p>
                  <div className="summary-grid compact-summary">
                    <article>
                      <span>Quality score</span>
                      <strong>{numberOrDash(selectedSavedSession.quality_score)}</strong>
                      <p>{selectedSavedSession.total_issue_count} issues</p>
                    </article>
                    <article>
                      <span>Rules</span>
                      <strong>{selectedSavedSession.selected_rules_count}</strong>
                      <p>selected rules</p>
                    </article>
                  </div>
                  <dl className="detail-list">
                    <div>
                      <dt>Selected rules</dt>
                      <dd>{selectedSavedSession.selected_rules.join(", ")}</dd>
                    </div>
                    <div>
                      <dt>Structure</dt>
                      <dd>
                        {String(
                          selectedSavedSession.structure_summary.detected_column_count ?? "-",
                        )}{" "}
                        columns,{" "}
                        {String(selectedSavedSession.structure_summary.preview_row_count ?? "-")}{" "}
                        preview rows
                      </dd>
                    </div>
                    <div>
                      <dt>Cleaning</dt>
                      <dd>
                        Rows {numberOrDash(selectedSavedSession.rows_before)} {"->"}{" "}
                        {numberOrDash(selectedSavedSession.rows_after)}, columns{" "}
                        {numberOrDash(selectedSavedSession.columns_before)} {"->"}{" "}
                        {numberOrDash(selectedSavedSession.columns_after)}
                      </dd>
                    </div>
                    <div>
                      <dt>Export</dt>
                      <dd>{String(selectedSavedSession.export_summary.format ?? "CSV")}</dd>
                    </div>
                  </dl>
                  {selectedSavedSession.preview_snapshot && (
                    <div className="preview-panel">
                      <div className="preview-heading">
                        <h3>Saved cleaned preview snapshot</h3>
                        <p>Snapshot is stored as metadata, not the original file.</p>
                      </div>
                      <div className="table-scroll" role="region" aria-label="Saved preview table">
                        <table>
                          <thead>
                            <tr>
                              {Array.isArray(selectedSavedSession.preview_snapshot.columns) &&
                                selectedSavedSession.preview_snapshot.columns.map((column) => (
                                  <th key={String(column)}>{String(column)}</th>
                                ))}
                            </tr>
                          </thead>
                          <tbody>
                            {Array.isArray(selectedSavedSession.preview_snapshot.rows) &&
                              selectedSavedSession.preview_snapshot.rows.map((row, rowIndex) => (
                                <tr key={`saved-${rowIndex}`}>
                                  {Array.isArray(row) &&
                                    row.map((cell, cellIndex) => (
                                      <td key={`${cellIndex}-${String(cell)}`}>{String(cell)}</td>
                                    ))}
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                  <div className="saved-report-panel" aria-label="Saved report replay panel">
                    <div>
                      <span className="status-label">HTML</span>
                      <h3>Open Saved HTML Report</h3>
                      <p>
                        Generate a standalone report from saved structure, quality, cleaning,
                        and export metadata. The original file is not required or stored.
                      </p>
                    </div>
                    <button
                      className="secondary-action"
                      type="button"
                      disabled={isGeneratingSavedReport}
                      onClick={handleOpenSavedSessionReport}
                    >
                      {isGeneratingSavedReport ? "Generating saved report..." : "Open Saved HTML Report"}
                    </button>
                    {savedReportSuccessMessage && (
                      <p className="export-status success">{savedReportSuccessMessage}</p>
                    )}
                    {savedReportErrorMessage && (
                      <p className="export-status error">{savedReportErrorMessage}</p>
                    )}
                    <p className="future-note">
                      Saved report replay is metadata-based. It does not reprocess the original file
                      or regenerate cleaned CSV from history.
                    </p>
                  </div>
                  <p className="future-note">
                    Saved history is local only. Cloud sync, authentication, and saved source files
                    are not implemented.
                  </p>
                </article>
              )}
            </div>
          )}
        </div>
      </section>

      <section className="workflow" aria-labelledby="workflow-title">
        <div className="section-heading">
          <p className="eyebrow">Workflow</p>
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
