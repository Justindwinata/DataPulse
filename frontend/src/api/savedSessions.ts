export type JsonObject = Record<string, unknown>;

export type SavedCleaningSessionCreate = {
  source_filename: string;
  detected_extension: string;
  content_type: string | null;
  file_size_bytes: number;
  selected_sheet_name: string | null;
  structure_summary: JsonObject;
  quality_summary: JsonObject;
  selected_rules: string[];
  cleaning_summary: JsonObject;
  rule_effects: JsonObject[];
  export_summary: JsonObject;
  report_summary: JsonObject;
  preview_snapshot?: JsonObject | null;
};

export type SavedCleaningSessionSummary = {
  id: number;
  source_filename: string;
  detected_extension: string;
  selected_sheet_name: string | null;
  quality_score: number | null;
  total_issue_count: number;
  selected_rules_count: number;
  rows_before: number | null;
  rows_after: number | null;
  columns_before: number | null;
  columns_after: number | null;
  created_at: string;
  updated_at: string;
};

export type SavedCleaningSessionDetail = SavedCleaningSessionSummary & {
  content_type: string | null;
  file_size_bytes: number;
  structure_summary: JsonObject;
  quality_summary: JsonObject;
  selected_rules: string[];
  cleaning_summary: JsonObject;
  rule_effects: JsonObject[];
  export_summary: JsonObject;
  report_summary: JsonObject;
  preview_snapshot: JsonObject | null;
  storage_note: string;
};

export type SavedCleaningSessionListResponse = {
  sessions: SavedCleaningSessionSummary[];
  total_count: number;
};

export class SavedSessionsError extends Error {
  constructor(message = "Saved sessions request failed. Confirm the backend is running and try again.") {
    super(message);
    this.name = "SavedSessionsError";
  }
}

const defaultApiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function createSession(
  payload: SavedCleaningSessionCreate,
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<SavedCleaningSessionDetail> {
  return requestJson<SavedCleaningSessionDetail>(`${apiBaseUrl}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function listSessions(
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<SavedCleaningSessionListResponse> {
  return requestJson<SavedCleaningSessionListResponse>(`${apiBaseUrl}/sessions`);
}

export async function getSession(
  sessionId: number,
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<SavedCleaningSessionDetail> {
  return requestJson<SavedCleaningSessionDetail>(`${apiBaseUrl}/sessions/${sessionId}`);
}

export async function deleteSession(
  sessionId: number,
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/sessions/${sessionId}`, { method: "DELETE" });
  } catch (error) {
    throw new SavedSessionsError();
  }
  if (!response.ok) {
    throw new SavedSessionsError(`Saved sessions request failed with status ${response.status}.`);
  }
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch (error) {
    throw new SavedSessionsError();
  }
  if (!response.ok) {
    throw new SavedSessionsError(`Saved sessions request failed with status ${response.status}.`);
  }
  try {
    return (await response.json()) as T;
  } catch (error) {
    throw new SavedSessionsError("Saved sessions returned an unreadable response.");
  }
}
