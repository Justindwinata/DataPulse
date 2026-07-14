import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import {
  detectFileStructure,
  type StructureDetectionResult,
} from "./api/structureDetection";
import {
  detectDataQuality,
  type DataQualityResult,
} from "./api/dataQuality";
import {
  generateCleaningPreview,
  type CleaningPreviewResult,
} from "./api/cleaningPreview";
import { exportCleanedCsv } from "./api/cleanedCsvExport";
import { generateCleaningReport } from "./api/cleaningReport";
import {
  createSession,
  deleteSession,
  generateSavedSessionReport,
  getSession,
  listSessions,
} from "./api/savedSessions";
import { validateUploadFile, type FileUploadValidationResponse } from "./api/uploadValidation";

vi.mock("./api/uploadValidation", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/uploadValidation")>();
  return {
    ...actual,
    validateUploadFile: vi.fn(),
  };
});

vi.mock("./api/structureDetection", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/structureDetection")>();
  return {
    ...actual,
    detectFileStructure: vi.fn(),
  };
});

vi.mock("./api/dataQuality", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/dataQuality")>();
  return {
    ...actual,
    detectDataQuality: vi.fn(),
  };
});

vi.mock("./api/cleaningPreview", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/cleaningPreview")>();
  return {
    ...actual,
    generateCleaningPreview: vi.fn(),
  };
});

vi.mock("./api/cleanedCsvExport", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/cleanedCsvExport")>();
  return {
    ...actual,
    exportCleanedCsv: vi.fn(),
  };
});

vi.mock("./api/cleaningReport", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/cleaningReport")>();
  return {
    ...actual,
    generateCleaningReport: vi.fn(),
  };
});

vi.mock("./api/savedSessions", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api/savedSessions")>();
  return {
    ...actual,
    createSession: vi.fn(),
    deleteSession: vi.fn(),
    generateSavedSessionReport: vi.fn(),
    getSession: vi.fn(),
    listSessions: vi.fn(),
  };
});

const acceptedResponse: FileUploadValidationResponse = {
  original_filename: "messy.csv",
  safe_filename: "messy.csv",
  detected_extension: "csv",
  content_type: "text/csv",
  file_size_bytes: 18,
  max_size_bytes: 10 * 1024 * 1024,
  is_supported: true,
  validation_status: "accepted",
  validation_messages: ["File extension is supported.", "File size is within the 10 MB limit."],
  next_step: "structure_detection",
  structure_detection_available: false,
};

const rejectedResponse: FileUploadValidationResponse = {
  original_filename: "document.pdf",
  safe_filename: "document.pdf",
  detected_extension: "pdf",
  content_type: "application/pdf",
  file_size_bytes: 1024,
  max_size_bytes: 10 * 1024 * 1024,
  is_supported: false,
  validation_status: "rejected",
  validation_messages: [
    "Unsupported file extension. Supported formats are CSV, TSV, TXT, XLSX, and XLS.",
  ],
  next_step: "upload_supported_file",
  structure_detection_available: false,
};

const excelAcceptedResponse: FileUploadValidationResponse = {
  ...acceptedResponse,
  original_filename: "workbook.xlsx",
  safe_filename: "workbook.xlsx",
  detected_extension: "xlsx",
  content_type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
};

const structureResponse: StructureDetectionResult = {
  original_filename: "messy.csv",
  safe_filename: "messy.csv",
  detected_extension: "csv",
  file_size_bytes: 18,
  content_type: "text/csv",
  structure_status: "detected",
  delimiter: {
    detected_delimiter: ",",
    delimiter_label: "comma",
    delimiter_confidence: "high",
    detection_reason: "Comma produced the most consistent sampled row widths.",
  },
  workbook: null,
  selected_sheet_name: null,
  has_detected_header: true,
  header_row_index: 0,
  column_names: ["name", "total"],
  generated_column_names: false,
  detected_column_count: 2,
  sampled_row_count: 2,
  preview_row_count: 1,
  total_row_count_calculated: false,
  total_row_count: null,
  warnings: [
    {
      code: "empty_rows_in_sample",
      message: "Empty rows were detected in the sampled file.",
      severity: "warning",
    },
  ],
  preview: {
    columns: ["name", "total"],
    rows: [["Ada", "10"]],
  },
  next_step: "quality_issue_detection",
};

const workbookDiscoveryResponse: StructureDetectionResult = {
  original_filename: "workbook.xlsx",
  safe_filename: "workbook.xlsx",
  detected_extension: "xlsx",
  file_size_bytes: 4096,
  content_type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  structure_status: "sheet_selection_required",
  delimiter: null,
  workbook: {
    workbook_type: "xlsx",
    sheet_names: ["Sales", "Customers"],
    sheet_count: 2,
    default_sheet_name: "Sales",
    sheets: [
      { sheet_name: "Sales", sheet_index: 0, max_row: 2, max_column: 2, is_empty: false },
      { sheet_name: "Customers", sheet_index: 1, max_row: 1, max_column: 1, is_empty: false },
    ],
  },
  selected_sheet_name: null,
  has_detected_header: false,
  header_row_index: null,
  column_names: [],
  generated_column_names: false,
  detected_column_count: 0,
  sampled_row_count: 0,
  preview_row_count: 0,
  total_row_count_calculated: false,
  total_row_count: null,
  warnings: [
    {
      code: "excel_formatting_not_preserved",
      message:
        "Excel formatting, formulas, merged cell behavior, charts, and pivot tables are not preserved in preview.",
      severity: "info",
    },
  ],
  preview: null,
  next_step: "select_excel_sheet",
};

const excelPreviewResponse: StructureDetectionResult = {
  ...structureResponse,
  original_filename: "workbook.xlsx",
  safe_filename: "workbook.xlsx",
  detected_extension: "xlsx",
  content_type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  delimiter: null,
  workbook: workbookDiscoveryResponse.workbook,
  selected_sheet_name: "Sales",
  column_names: ["customer", "amount"],
  preview: {
    columns: ["customer", "amount"],
    rows: [["Ari", "1200"]],
  },
};

const qualityResponse: DataQualityResult = {
  quality_status: "profiled",
  original_filename: "messy.csv",
  safe_filename: "messy.csv",
  detected_extension: "csv",
  selected_sheet_name: null,
  sampled_row_count: 2,
  detected_column_count: 2,
  total_issue_count: 2,
  severity_counts: {
    info: 1,
    warning: 1,
    critical: 0,
  },
  quality_score: 91,
  issues: [
    {
      code: "missing_values",
      title: "Missing values detected",
      message: "Some columns contain empty values in the sampled data.",
      severity: "warning",
      affected_columns: ["amount"],
      affected_row_count: 1,
      suggested_cleaning_rule: null,
    },
    {
      code: "leading_trailing_whitespace",
      title: "Leading or trailing whitespace detected",
      message: "Some sampled values contain whitespace around the visible value.",
      severity: "info",
      affected_columns: ["name"],
      affected_row_count: 1,
      suggested_cleaning_rule: "trim_whitespace",
    },
    {
      code: "numeric_values_as_text",
      title: "Possible numeric columns stored as text",
      message: "Some sampled columns contain numeric-looking text values.",
      severity: "info",
      affected_columns: ["amount"],
      affected_row_count: null,
      suggested_cleaning_rule: "convert_numeric_columns",
    },
  ],
  columns: [
    {
      column_name: "name",
      column_index: 0,
      non_empty_count: 2,
      missing_count: 0,
      missing_percentage: 0,
      inferred_type: "text",
      unique_count: 2,
      sample_values: ["Ari", "Justin"],
      issues: [],
    },
    {
      column_name: "amount",
      column_index: 1,
      non_empty_count: 1,
      missing_count: 1,
      missing_percentage: 50,
      inferred_type: "number",
      unique_count: 1,
      sample_values: ["1200"],
      issues: ["missing_values", "numeric_values_as_text"],
    },
  ],
  messages: [],
  next_step: "cleaning_rules",
};

const excelQualityResponse: DataQualityResult = {
  ...qualityResponse,
  original_filename: "workbook.xlsx",
  safe_filename: "workbook.xlsx",
  detected_extension: "xlsx",
  selected_sheet_name: "Sales",
};

const cleaningPreviewResponse: CleaningPreviewResult = {
  cleaning_status: "preview_generated",
  original_filename: "messy.csv",
  safe_filename: "messy.csv",
  detected_extension: "csv",
  selected_sheet_name: null,
  applied_rules: ["trim_whitespace", "remove_empty_rows"],
  before_summary: {
    row_count: 3,
    column_count: 2,
    empty_rows_count: 1,
    duplicate_rows_count: 0,
    empty_columns_count: 0,
  },
  after_summary: {
    row_count: 2,
    column_count: 2,
    removed_empty_rows_count: 1,
    removed_duplicate_rows_count: 0,
    dropped_empty_columns_count: 0,
    renamed_columns_count: 0,
  },
  rule_effects: [
    {
      rule: "trim_whitespace",
      label: "Trim whitespace",
      status: "applied",
      message: "Trimmed whitespace in 1 sampled cells.",
      affected_rows: 1,
      affected_columns: 1,
    },
    {
      rule: "remove_empty_rows",
      label: "Remove empty rows",
      status: "applied",
      message: "Removed 1 empty rows from the preview sample.",
      affected_rows: 1,
      affected_columns: 0,
    },
  ],
  cleaned_preview: {
    columns: ["name", "amount"],
    rows: [["Ari", "1200"]],
  },
  warnings: [
    {
      code: "sample_based_preview",
      message: "Cleaning preview is generated from a bounded sample.",
      severity: "info",
    },
  ],
  next_step: "download_cleaned_csv",
};

const excelCleaningPreviewResponse: CleaningPreviewResult = {
  ...cleaningPreviewResponse,
  original_filename: "workbook.xlsx",
  safe_filename: "workbook.xlsx",
  detected_extension: "xlsx",
  selected_sheet_name: "Sales",
};

const savedSessionDetail = {
  id: 7,
  source_filename: "messy.csv",
  detected_extension: "csv",
  selected_sheet_name: null,
  quality_score: 91,
  total_issue_count: 2,
  selected_rules_count: 2,
  rows_before: 3,
  rows_after: 2,
  columns_before: 2,
  columns_after: 2,
  created_at: "2026-07-14T00:00:00Z",
  updated_at: "2026-07-14T00:00:00Z",
  content_type: "text/csv",
  file_size_bytes: 18,
  structure_summary: {},
  quality_summary: {},
  selected_rules: ["trim_whitespace", "remove_empty_rows"],
  cleaning_summary: {},
  rule_effects: [],
  export_summary: {},
  report_summary: {},
  preview_snapshot: null,
  storage_note: "Original uploaded files are not stored.",
};

describe("App", () => {
  beforeEach(() => {
    vi.mocked(validateUploadFile).mockReset();
    vi.mocked(detectFileStructure).mockReset();
    vi.mocked(detectDataQuality).mockReset();
    vi.mocked(generateCleaningPreview).mockReset();
    vi.mocked(exportCleanedCsv).mockReset();
    vi.mocked(generateCleaningReport).mockReset();
    vi.mocked(createSession).mockReset();
    vi.mocked(deleteSession).mockReset();
    vi.mocked(generateSavedSessionReport).mockReset();
    vi.mocked(getSession).mockReset();
    vi.mocked(listSessions).mockReset();
    vi.stubGlobal("confirm", vi.fn(() => true));
  });

  it("renders the DataPulse product foundation screen", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "DataPulse" })).toBeInTheDocument();
    expect(screen.getByText("Messy CSV & Excel Cleaner Studio")).toBeInTheDocument();
    expect(screen.getByText("Choose a tabular file")).toBeInTheDocument();
    expect(screen.getByText("Rule-Based Cleaning")).toBeInTheDocument();
    expect(screen.getByText("Cleaned CSV Export")).toBeInTheDocument();
    expect(screen.queryByText(/restore file/i)).not.toBeInTheDocument();
  });

  it("shows selected file metadata", () => {
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });

    expect(screen.getByText("messy.csv")).toBeInTheDocument();
    expect(screen.getByText("text/csv")).toBeInTheDocument();
    expect(screen.getByText("18 B")).toBeInTheDocument();
  });

  it("renders validation success result", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByText("Accepted")).toBeInTheDocument();
    });
    expect(screen.getByText("File extension is supported.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
  });

  it("renders validation rejection result", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(rejectedResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["pdf"], "document.pdf", { type: "application/pdf" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByText("Rejected")).toBeInTheDocument();
    });
    expect(screen.getByText(/Unsupported file extension/)).toBeInTheDocument();
  });

  it("renders backend error state", async () => {
    vi.mocked(validateUploadFile).mockRejectedValue(new Error("backend down"));
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByText("Validation request failed")).toBeInTheDocument();
    });
    expect(screen.getByText(/Confirm the backend is running/)).toBeInTheDocument();
  });

  it("renders structure summary, warnings, and preview table", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByText("Raw preview")).toBeInTheDocument();
    });
    expect(screen.getByText("comma")).toBeInTheDocument();
    expect(screen.getByText("empty_rows_in_sample")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "name" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "Ada" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
  });

  it("renders Excel sheet selector after workbook discovery", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(excelAcceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(workbookDiscoveryResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["workbook"], "workbook.xlsx")],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(
        screen.getByText(/Excel workbook detected/),
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByText("Choose a sheet to preview")).toBeInTheDocument();
    });
    expect(screen.getByLabelText("Sheet")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Preview selected sheet" })).toBeInTheDocument();
    expect(screen.getByText("excel_formatting_not_preserved")).toBeInTheDocument();
  });

  it("renders selected Excel sheet preview", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(excelAcceptedResponse);
    vi.mocked(detectFileStructure)
      .mockResolvedValueOnce(workbookDiscoveryResponse)
      .mockResolvedValueOnce(excelPreviewResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["workbook"], "workbook.xlsx")],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Preview selected sheet" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Preview selected sheet" }));

    await waitFor(() => {
      expect(screen.getByText("Selected worksheet")).toBeInTheDocument();
    });
    expect(screen.getByRole("columnheader", { name: "customer" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "Ari" })).toBeInTheDocument();
    expect(vi.mocked(detectFileStructure)).toHaveBeenLastCalledWith(expect.any(File), "Sales");
  });

  it("renders quality summary, issue cards, and column profile", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(qualityResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByText("Quality score")).toBeInTheDocument();
    });
    expect(screen.getByText("91")).toBeInTheDocument();
    expect(screen.getByText("Missing values detected")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Column" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "amount" })).toBeInTheDocument();
    expect(screen.getByText(/DataPulse has not modified your file yet/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /download/i })).not.toBeInTheDocument();
  });

  it("renders cleaning rules and cleaned preview after quality analysis", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(qualityResponse);
    vi.mocked(generateCleaningPreview).mockResolvedValue(cleaningPreviewResponse);
    vi.mocked(exportCleanedCsv).mockResolvedValue({
      blob: new Blob(["name\nAri\n"], { type: "text/csv" }),
      filename: "messy_cleaned.csv",
    });
    const createObjectUrl = vi
      .spyOn(URL, "createObjectURL")
      .mockReturnValue("blob:datapulse-cleaned");
    const revokeObjectUrl = vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => undefined);
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByText("Select rules and preview cleaned data")).toBeInTheDocument();
    });
    expect(screen.getAllByText("Recommended").length).toBeGreaterThan(0);
    expect(screen.getByLabelText(/Trim whitespace/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Generate Cleaned Preview" }));

    await waitFor(() => {
      expect(screen.getByText("Rows before")).toBeInTheDocument();
    });
    expect(screen.getByText("Rule effects")).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Cleaned preview table" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "Ari" })).toBeInTheDocument();
    expect(screen.getByText("Download cleaned CSV")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open HTML Cleaning Report" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save Cleaning Session" })).toBeInTheDocument();
    expect(screen.getAllByText(/Original uploaded files are not stored/).length).toBeGreaterThan(0);
    expect(vi.mocked(generateCleaningPreview)).toHaveBeenCalledWith(
      expect.any(File),
      expect.arrayContaining(["trim_whitespace"]),
      undefined,
    );

    fireEvent.click(screen.getByRole("button", { name: "Download Cleaned CSV" }));

    await waitFor(() => {
      expect(screen.getByText("Downloaded messy_cleaned.csv")).toBeInTheDocument();
    });
    expect(vi.mocked(exportCleanedCsv)).toHaveBeenCalledWith(
      expect.any(File),
      expect.arrayContaining(["trim_whitespace"]),
      undefined,
    );
    expect(createObjectUrl).toHaveBeenCalled();
    expect(clickSpy).toHaveBeenCalled();
    expect(revokeObjectUrl).toHaveBeenCalledWith("blob:datapulse-cleaned");
  });

  it("saves current cleaning session metadata after cleaned preview", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(qualityResponse);
    vi.mocked(generateCleaningPreview).mockResolvedValue(cleaningPreviewResponse);
    vi.mocked(createSession).mockResolvedValue(savedSessionDetail);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Generate Cleaned Preview" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Cleaned Preview" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Save Cleaning Session" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Save Cleaning Session" }));

    await waitFor(() => {
      expect(screen.getByText("Saved session #7 locally.")).toBeInTheDocument();
    });
    expect(vi.mocked(createSession)).toHaveBeenCalledWith(
      expect.objectContaining({
        source_filename: "messy.csv",
        detected_extension: "csv",
        selected_rules: expect.arrayContaining(["trim_whitespace"]),
        preview_snapshot: cleaningPreviewResponse.cleaned_preview,
      }),
    );
    const payload = vi.mocked(createSession).mock.calls[0][0];
    expect(payload).not.toHaveProperty("file");
    expect(payload.structure_summary).toMatchObject({ detected_column_count: 2 });
    expect(payload.quality_summary).toMatchObject({ quality_score: 91 });
  });

  it("renders save session error state", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(qualityResponse);
    vi.mocked(generateCleaningPreview).mockResolvedValue(cleaningPreviewResponse);
    vi.mocked(createSession).mockRejectedValue(new Error("backend down"));
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Generate Cleaned Preview" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Cleaned Preview" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Save Cleaning Session" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Save Cleaning Session" }));

    await waitFor(() => {
      expect(screen.getByText(/Saving the cleaning session failed/)).toBeInTheDocument();
    });
  });

  it("opens an HTML cleaning report after cleaned preview", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(qualityResponse);
    vi.mocked(generateCleaningPreview).mockResolvedValue(cleaningPreviewResponse);
    vi.mocked(generateCleaningReport).mockResolvedValue(
      new Blob(["<html>report</html>"], { type: "text/html" }),
    );
    const createObjectUrl = vi
      .spyOn(URL, "createObjectURL")
      .mockReturnValue("blob:datapulse-report");
    const openWindow = vi.fn(() => ({ closed: false }) as Window);
    vi.stubGlobal("open", openWindow);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Generate Cleaned Preview" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Cleaned Preview" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Open HTML Cleaning Report" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Open HTML Cleaning Report" }));

    await waitFor(() => {
      expect(screen.getByText("Opened HTML cleaning report.")).toBeInTheDocument();
    });
    expect(vi.mocked(generateCleaningReport)).toHaveBeenCalledWith(
      expect.any(File),
      expect.arrayContaining(["trim_whitespace"]),
      undefined,
    );
    expect(createObjectUrl).toHaveBeenCalled();
    expect(openWindow).toHaveBeenCalledWith("blob:datapulse-report", "_blank", "noopener,noreferrer");
    expect(screen.queryByText(/Previous reports/i)).not.toBeInTheDocument();
  });

  it("runs quality analysis for the selected Excel sheet", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(excelAcceptedResponse);
    vi.mocked(detectFileStructure)
      .mockResolvedValueOnce(workbookDiscoveryResponse)
      .mockResolvedValueOnce(excelPreviewResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(excelQualityResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["workbook"], "workbook.xlsx")],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Preview selected sheet" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Preview selected sheet" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByText("Quality score")).toBeInTheDocument();
    });
    expect(vi.mocked(detectDataQuality)).toHaveBeenLastCalledWith(expect.any(File), "Sales");
  });

  it("runs cleaning preview for the selected Excel sheet", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(excelAcceptedResponse);
    vi.mocked(detectFileStructure)
      .mockResolvedValueOnce(workbookDiscoveryResponse)
      .mockResolvedValueOnce(excelPreviewResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(excelQualityResponse);
    vi.mocked(generateCleaningPreview).mockResolvedValue(excelCleaningPreviewResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["workbook"], "workbook.xlsx")],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Preview selected sheet" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Preview selected sheet" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Generate Cleaned Preview" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Cleaned Preview" }));

    await waitFor(() => {
      expect(screen.getByText("Cleaned preview")).toBeInTheDocument();
    });
    expect(screen.getByText(/Excel formatting, formulas, charts/)).toBeInTheDocument();
    expect(vi.mocked(generateCleaningPreview)).toHaveBeenLastCalledWith(
      expect.any(File),
      expect.any(Array),
      "Sales",
    );
  });

  it("renders cleaned CSV export error state", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(qualityResponse);
    vi.mocked(generateCleaningPreview).mockResolvedValue(cleaningPreviewResponse);
    vi.mocked(exportCleanedCsv).mockRejectedValue(new Error("backend down"));
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Generate Cleaned Preview" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Cleaned Preview" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Download Cleaned CSV" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Download Cleaned CSV" }));

    await waitFor(() => {
      expect(screen.getByText(/Cleaned CSV export failed/)).toBeInTheDocument();
    });
  });

  it("renders empty saved history state", async () => {
    vi.mocked(listSessions).mockResolvedValue({ sessions: [], total_count: 0 });
    render(<App />);

    expect(screen.getByText("Saved cleaning sessions")).toBeInTheDocument();
    expect(
      screen.getByText("Save a cleaning session to review your data preparation history."),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Load Saved Sessions" }));

    await waitFor(() => {
      expect(vi.mocked(listSessions)).toHaveBeenCalled();
    });
  });

  it("renders saved sessions list and detail", async () => {
    vi.mocked(listSessions).mockResolvedValue({ sessions: [savedSessionDetail], total_count: 1 });
    vi.mocked(getSession).mockResolvedValue(savedSessionDetail);
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Load Saved Sessions" }));

    await waitFor(() => {
      expect(screen.getByRole("region", { name: "Saved sessions table" })).toBeInTheDocument();
    });
    expect(screen.getByRole("cell", { name: "messy.csv" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "91" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "View Detail" }));

    await waitFor(() => {
      expect(screen.getByLabelText("Saved session detail")).toBeInTheDocument();
    });
    expect(screen.getAllByText(/Original uploaded files are not stored/).length).toBeGreaterThan(0);
    expect(screen.getByText(/trim_whitespace/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open Saved HTML Report" })).toBeInTheDocument();
    expect(screen.getByText(/Saved report replay is metadata-based/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /PDF/i })).not.toBeInTheDocument();
  });

  it("opens a saved HTML report from session detail", async () => {
    vi.mocked(listSessions).mockResolvedValue({ sessions: [savedSessionDetail], total_count: 1 });
    vi.mocked(getSession).mockResolvedValue(savedSessionDetail);
    vi.mocked(generateSavedSessionReport).mockResolvedValue(
      new Blob(["<html>saved report</html>"], { type: "text/html" }),
    );
    const createObjectUrl = vi
      .spyOn(URL, "createObjectURL")
      .mockReturnValue("blob:datapulse-saved-report");
    const openWindow = vi.fn(() => ({ closed: false }) as Window);
    vi.stubGlobal("open", openWindow);
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Load Saved Sessions" }));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "View Detail" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "View Detail" }));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Open Saved HTML Report" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Open Saved HTML Report" }));

    await waitFor(() => {
      expect(screen.getByText("Opened saved HTML report.")).toBeInTheDocument();
    });
    expect(vi.mocked(generateSavedSessionReport)).toHaveBeenCalledWith(7);
    expect(createObjectUrl).toHaveBeenCalled();
    expect(openWindow).toHaveBeenCalledWith("blob:datapulse-saved-report", "_blank", "noopener,noreferrer");
  });

  it("renders saved HTML report error state", async () => {
    vi.mocked(listSessions).mockResolvedValue({ sessions: [savedSessionDetail], total_count: 1 });
    vi.mocked(getSession).mockResolvedValue(savedSessionDetail);
    vi.mocked(generateSavedSessionReport).mockRejectedValue(new Error("backend down"));
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Load Saved Sessions" }));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "View Detail" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "View Detail" }));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Open Saved HTML Report" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Open Saved HTML Report" }));

    await waitFor(() => {
      expect(screen.getByText(/Saved HTML report generation failed/)).toBeInTheDocument();
    });
  });

  it("deletes a saved session after confirmation", async () => {
    vi.mocked(listSessions).mockResolvedValue({ sessions: [savedSessionDetail], total_count: 1 });
    vi.mocked(getSession).mockResolvedValue(savedSessionDetail);
    vi.mocked(deleteSession).mockResolvedValue(undefined);
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Load Saved Sessions" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "View Detail" }));
    await waitFor(() => {
      expect(screen.getByLabelText("Saved session detail")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() => {
      expect(screen.getByText("Deleted saved session #7.")).toBeInTheDocument();
    });
    expect(vi.mocked(deleteSession)).toHaveBeenCalledWith(7);
    expect(screen.queryByLabelText("Saved session detail")).not.toBeInTheDocument();
  });

  it("renders saved history error state", async () => {
    vi.mocked(listSessions).mockRejectedValue(new Error("backend down"));
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Load Saved Sessions" }));

    await waitFor(() => {
      expect(screen.getByText(/Loading saved sessions failed/)).toBeInTheDocument();
    });
  });

  it("renders cleaning preview backend error state", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    vi.mocked(detectDataQuality).mockResolvedValue(qualityResponse);
    vi.mocked(generateCleaningPreview).mockRejectedValue(new Error("backend down"));
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Generate Cleaned Preview" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Cleaned Preview" }));

    await waitFor(() => {
      expect(screen.getByText("Cleaning preview request failed")).toBeInTheDocument();
    });
    expect(screen.getByText(/Confirm the backend is running/)).toBeInTheDocument();
  });

  it("renders quality backend error state", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockResolvedValue(structureResponse);
    vi.mocked(detectDataQuality).mockRejectedValue(new Error("backend down"));
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Analyze Data Quality" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Analyze Data Quality" }));

    await waitFor(() => {
      expect(screen.getByText("Data quality request failed")).toBeInTheDocument();
    });
    expect(screen.getByText(/Confirm the backend is running/)).toBeInTheDocument();
  });

  it("renders structure detection backend error state", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(acceptedResponse);
    vi.mocked(detectFileStructure).mockRejectedValue(new Error("backend down"));
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" })],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Detect Structure" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detect Structure" }));

    await waitFor(() => {
      expect(screen.getByText("Structure detection request failed")).toBeInTheDocument();
    });
    expect(screen.getByText(/Confirm the backend is running/)).toBeInTheDocument();
  });
});
