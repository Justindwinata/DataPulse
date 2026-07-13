import type { CleaningRuleCode } from "./cleaningPreview";

export type CleanedCsvDownload = {
  blob: Blob;
  filename: string;
};

export class CleanedCsvExportError extends Error {
  constructor(message = "Cleaned CSV export failed. Confirm the backend is running and try again.") {
    super(message);
    this.name = "CleanedCsvExportError";
  }
}

export async function exportCleanedCsv(
  file: File,
  rules: CleaningRuleCode[],
  sheetName?: string,
  apiBaseUrl: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
): Promise<CleanedCsvDownload> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("rules", JSON.stringify(rules));
  if (sheetName) {
    formData.append("sheet_name", sheetName);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/files/export-cleaned-csv`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new CleanedCsvExportError();
  }

  if (!response.ok) {
    throw new CleanedCsvExportError(`Cleaned CSV export failed with status ${response.status}.`);
  }

  try {
    return {
      blob: await response.blob(),
      filename: filenameFromContentDisposition(response.headers.get("content-disposition")),
    };
  } catch (error) {
    throw new CleanedCsvExportError("Cleaned CSV export returned an unreadable response.");
  }
}

export function filenameFromContentDisposition(header: string | null): string {
  if (!header) {
    return "datapulse_cleaned.csv";
  }
  const match = /filename="?([^";]+)"?/i.exec(header);
  return match?.[1] ?? "datapulse_cleaned.csv";
}
