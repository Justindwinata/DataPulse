import type { CleaningRuleCode } from "./cleaningPreview";

export class CleaningReportError extends Error {
  constructor(message = "HTML cleaning report generation failed. Confirm the backend is running and try again.") {
    super(message);
    this.name = "CleaningReportError";
  }
}

export async function generateCleaningReport(
  file: File,
  rules: CleaningRuleCode[],
  sheetName?: string,
  apiBaseUrl: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
): Promise<Blob> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("rules", JSON.stringify(rules));
  if (sheetName) {
    formData.append("sheet_name", sheetName);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/files/cleaning-report.html`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new CleaningReportError();
  }

  if (!response.ok) {
    throw new CleaningReportError(`HTML cleaning report generation failed with status ${response.status}.`);
  }

  try {
    return await response.blob();
  } catch (error) {
    throw new CleaningReportError("HTML cleaning report returned an unreadable response.");
  }
}
