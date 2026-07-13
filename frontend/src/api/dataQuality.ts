export type QualityStatus = "profiled" | "rejected" | "sheet_selection_required";
export type IssueSeverity = "info" | "warning" | "critical";
export type InferredColumnType = "text" | "number" | "date" | "boolean" | "mixed" | "empty";
export type QualityNextStep = "cleaning_rules" | "select_excel_sheet" | "upload_supported_file";

export type SeverityCounts = {
  info: number;
  warning: number;
  critical: number;
};

export type DataQualityIssue = {
  code: string;
  title: string;
  message: string;
  severity: IssueSeverity;
  affected_columns: string[];
  affected_row_count: number | null;
  suggested_cleaning_rule: string | null;
};

export type ColumnProfile = {
  column_name: string;
  column_index: number;
  non_empty_count: number;
  missing_count: number;
  missing_percentage: number;
  inferred_type: InferredColumnType;
  unique_count: number;
  sample_values: string[];
  issues: string[];
};

export type DataQualityResult = {
  quality_status: QualityStatus;
  original_filename: string;
  safe_filename: string;
  detected_extension: string;
  selected_sheet_name: string | null;
  sampled_row_count: number;
  detected_column_count: number;
  total_issue_count: number;
  severity_counts: SeverityCounts;
  quality_score: number;
  issues: DataQualityIssue[];
  columns: ColumnProfile[];
  messages: string[];
  next_step: QualityNextStep;
};

export class DataQualityError extends Error {
  constructor(message = "Data quality analysis failed. Confirm the backend is running and try again.") {
    super(message);
    this.name = "DataQualityError";
  }
}

export async function detectDataQuality(
  file: File,
  sheetName?: string,
  apiBaseUrl: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
): Promise<DataQualityResult> {
  const formData = new FormData();
  formData.append("file", file);
  if (sheetName) {
    formData.append("sheet_name", sheetName);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/files/detect-quality`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new DataQualityError();
  }

  if (!response.ok) {
    throw new DataQualityError(`Data quality analysis failed with status ${response.status}.`);
  }

  try {
    return (await response.json()) as DataQualityResult;
  } catch (error) {
    throw new DataQualityError("Data quality analysis returned an unreadable response.");
  }
}
