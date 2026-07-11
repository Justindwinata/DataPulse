export type StructureDetectionStatus = "detected" | "rejected" | "not_implemented";
export type DelimiterConfidence = "high" | "medium" | "low" | "unknown";
export type StructureWarningSeverity = "info" | "warning" | "error";
export type StructureNextStep =
  | "quality_issue_detection"
  | "upload_supported_file"
  | "wait_for_excel_support";

export type DelimiterDetection = {
  detected_delimiter: string | null;
  delimiter_label: string;
  delimiter_confidence: DelimiterConfidence;
  detection_reason: string;
};

export type StructureWarning = {
  code: string;
  message: string;
  severity: StructureWarningSeverity;
};

export type RawTablePreview = {
  columns: string[];
  rows: string[][];
};

export type StructureDetectionResult = {
  original_filename: string;
  safe_filename: string;
  detected_extension: string;
  file_size_bytes: number;
  content_type: string | null;
  structure_status: StructureDetectionStatus;
  delimiter: DelimiterDetection | null;
  has_detected_header: boolean;
  header_row_index: number | null;
  column_names: string[];
  generated_column_names: boolean;
  detected_column_count: number;
  sampled_row_count: number;
  preview_row_count: number;
  total_row_count_calculated: boolean;
  total_row_count: number | null;
  warnings: StructureWarning[];
  preview: RawTablePreview | null;
  next_step: StructureNextStep;
};

export class StructureDetectionError extends Error {
  constructor(message = "Structure detection failed. Confirm the backend is running and try again.") {
    super(message);
    this.name = "StructureDetectionError";
  }
}

export async function detectFileStructure(
  file: File,
  apiBaseUrl: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
): Promise<StructureDetectionResult> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/files/detect-structure`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new StructureDetectionError();
  }

  if (!response.ok) {
    throw new StructureDetectionError(`Structure detection failed with status ${response.status}.`);
  }

  try {
    return (await response.json()) as StructureDetectionResult;
  } catch (error) {
    throw new StructureDetectionError("Structure detection returned an unreadable response.");
  }
}
