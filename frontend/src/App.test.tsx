import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import {
  detectFileStructure,
  type StructureDetectionResult,
} from "./api/structureDetection";
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

describe("App", () => {
  beforeEach(() => {
    vi.mocked(validateUploadFile).mockReset();
    vi.mocked(detectFileStructure).mockReset();
  });

  it("renders the DataPulse product foundation screen", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "DataPulse" })).toBeInTheDocument();
    expect(screen.getByText("Messy CSV & Excel Cleaner Studio")).toBeInTheDocument();
    expect(screen.getByText("Choose a tabular file")).toBeInTheDocument();
    expect(screen.getByText("Rule-Based Cleaning")).toBeInTheDocument();
    expect(screen.getByText("Cleaned CSV Export")).toBeInTheDocument();
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
  });

  it("renders Excel limitation message after accepted Excel validation", async () => {
    vi.mocked(validateUploadFile).mockResolvedValue(excelAcceptedResponse);
    render(<App />);

    fireEvent.change(screen.getByLabelText(/Choose a tabular file/i), {
      target: {
        files: [new File(["workbook"], "workbook.xlsx")],
      },
    });
    fireEvent.click(screen.getByRole("button", { name: "Validate upload" }));

    await waitFor(() => {
      expect(
        screen.getByText("Excel structure detection is planned for a later milestone."),
      ).toBeInTheDocument();
    });
    expect(screen.queryByRole("button", { name: "Detect Structure" })).not.toBeInTheDocument();
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
