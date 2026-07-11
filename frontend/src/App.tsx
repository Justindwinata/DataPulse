import { ChangeEvent, FormEvent, useState } from "react";

import {
  UploadValidationError,
  validateUploadFile,
  type FileUploadValidationResponse,
} from "./api/uploadValidation";

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

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] =
    useState<FileUploadValidationResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setValidationResult(null);
    setErrorMessage(null);
  };

  const handleValidate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) {
      setErrorMessage("Select a CSV, TSV, TXT, XLSX, or XLS file before validation.");
      return;
    }

    setIsValidating(true);
    setErrorMessage(null);
    setValidationResult(null);

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

  return (
    <main className="app-shell">
      <section className="hero" aria-labelledby="product-title">
        <div className="hero-copy">
          <p className="eyebrow">File intake validation</p>
          <h1 id="product-title">DataPulse</h1>
          <p className="subtitle">Messy CSV & Excel Cleaner Studio</p>
          <p className="description">
            Upload a tabular file and verify whether it can move forward to future
            structure detection. DP-0002 validates file metadata only; parsing and
            cleaning are not implemented yet.
          </p>
        </div>
        <div className="status-panel" aria-label="Current foundation status">
          <span className="status-label">DP-0002</span>
          <strong>Upload validation active</strong>
          <p>Supported: CSV, TSV, TXT, XLSX, and XLS up to 10 MB. Files are not stored.</p>
        </div>
      </section>

      <section className="upload-workspace" aria-labelledby="upload-title">
        <div className="section-heading">
          <p className="eyebrow">Validation workspace</p>
          <h2 id="upload-title">Check a file before structure detection</h2>
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
                  rows, detect delimiters, read Excel sheets, or clean data in this milestone.
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
                  {validationResult.structure_detection_available ? "yes" : "not yet"}.
                  Parsing, previews, cleaning, exports, and reports come later.
                </p>
              </div>
            )}
          </aside>
        </div>
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
