export type CleaningRuleCode =
  | "trim_whitespace"
  | "remove_empty_rows"
  | "remove_duplicate_rows"
  | "drop_empty_columns"
  | "standardize_column_names"
  | "generate_missing_column_names";

export type CleaningStatus = "preview_generated" | "rejected" | "sheet_selection_required";
export type CleaningRuleEffectStatus = "applied" | "no_effect" | "skipped";
export type CleaningWarningSeverity = "info" | "warning" | "error";
export type CleaningNextStep =
  | "download_cleaned_csv"
  | "select_excel_sheet"
  | "upload_supported_file";

export type CleaningSummaryBefore = {
  row_count: number;
  column_count: number;
  empty_rows_count: number;
  duplicate_rows_count: number;
  empty_columns_count: number;
};

export type CleaningSummaryAfter = {
  row_count: number;
  column_count: number;
  removed_empty_rows_count: number;
  removed_duplicate_rows_count: number;
  dropped_empty_columns_count: number;
  renamed_columns_count: number;
};

export type CleaningRuleEffect = {
  rule: CleaningRuleCode;
  label: string;
  status: CleaningRuleEffectStatus;
  message: string;
  affected_rows: number;
  affected_columns: number;
};

export type CleaningPreviewWarning = {
  code: string;
  message: string;
  severity: CleaningWarningSeverity;
};

export type CleanedTablePreview = {
  columns: string[];
  rows: string[][];
};

export type CleaningPreviewResult = {
  cleaning_status: CleaningStatus;
  original_filename: string;
  safe_filename: string;
  detected_extension: string;
  selected_sheet_name: string | null;
  applied_rules: CleaningRuleCode[];
  before_summary: CleaningSummaryBefore;
  after_summary: CleaningSummaryAfter;
  rule_effects: CleaningRuleEffect[];
  cleaned_preview: CleanedTablePreview;
  warnings: CleaningPreviewWarning[];
  next_step: CleaningNextStep;
};

export class CleaningPreviewError extends Error {
  constructor(message = "Cleaning preview failed. Confirm the backend is running and try again.") {
    super(message);
    this.name = "CleaningPreviewError";
  }
}

export async function generateCleaningPreview(
  file: File,
  rules: CleaningRuleCode[],
  sheetName?: string,
  apiBaseUrl: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
): Promise<CleaningPreviewResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("rules", JSON.stringify(rules));
  if (sheetName) {
    formData.append("sheet_name", sheetName);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/files/apply-cleaning-preview`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new CleaningPreviewError();
  }

  if (!response.ok) {
    throw new CleaningPreviewError(`Cleaning preview failed with status ${response.status}.`);
  }

  try {
    return (await response.json()) as CleaningPreviewResult;
  } catch (error) {
    throw new CleaningPreviewError("Cleaning preview returned an unreadable response.");
  }
}
