import type { CleaningRuleCode } from "./cleaningPreview";

export type WorkflowTemplateCreate = {
  name: string;
  description?: string | null;
  selected_rules: CleaningRuleCode[];
  source_session_id?: number | null;
  source_filename?: string | null;
};

export type WorkflowTemplateUpdate = {
  name?: string;
  description?: string | null;
  selected_rules?: CleaningRuleCode[];
};

export type WorkflowTemplateSummary = {
  id: number;
  name: string;
  description: string | null;
  selected_rules_count: number;
  source_session_id: number | null;
  source_filename: string | null;
  created_at: string;
  updated_at: string;
};

export type WorkflowTemplateDetail = WorkflowTemplateSummary & {
  selected_rules: CleaningRuleCode[];
  storage_note: string;
  new_upload_required_note: string;
};

export type WorkflowTemplateListResponse = {
  templates: WorkflowTemplateSummary[];
  total_count: number;
};

export class WorkflowTemplatesError extends Error {
  constructor(message = "Workflow templates request failed. Confirm the backend is running and try again.") {
    super(message);
    this.name = "WorkflowTemplatesError";
  }
}

const defaultApiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function createTemplate(
  payload: WorkflowTemplateCreate,
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<WorkflowTemplateDetail> {
  return requestJson<WorkflowTemplateDetail>(`${apiBaseUrl}/templates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function listTemplates(
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<WorkflowTemplateListResponse> {
  return requestJson<WorkflowTemplateListResponse>(`${apiBaseUrl}/templates`);
}

export async function getTemplate(
  templateId: number,
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<WorkflowTemplateDetail> {
  return requestJson<WorkflowTemplateDetail>(`${apiBaseUrl}/templates/${templateId}`);
}

export async function updateTemplate(
  templateId: number,
  payload: WorkflowTemplateUpdate,
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<WorkflowTemplateDetail> {
  return requestJson<WorkflowTemplateDetail>(`${apiBaseUrl}/templates/${templateId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function deleteTemplate(
  templateId: number,
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/templates/${templateId}`, { method: "DELETE" });
  } catch (error) {
    throw new WorkflowTemplatesError();
  }
  if (!response.ok) {
    throw new WorkflowTemplatesError(`Workflow templates request failed with status ${response.status}.`);
  }
}

export async function createTemplateFromSession(
  sessionId: number,
  payload: WorkflowTemplateCreate,
  apiBaseUrl: string = defaultApiBaseUrl,
): Promise<WorkflowTemplateDetail> {
  return requestJson<WorkflowTemplateDetail>(`${apiBaseUrl}/templates/from-session/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch (error) {
    throw new WorkflowTemplatesError();
  }
  if (!response.ok) {
    throw new WorkflowTemplatesError(`Workflow templates request failed with status ${response.status}.`);
  }
  try {
    return (await response.json()) as T;
  } catch (error) {
    throw new WorkflowTemplatesError("Workflow templates returned an unreadable response.");
  }
}
