import { afterEach, describe, expect, it, vi } from "vitest";

import {
  WorkflowTemplatesError,
  createTemplate,
  createTemplateFromSession,
  deleteTemplate,
  getTemplate,
  listTemplates,
  updateTemplate,
  type WorkflowTemplateCreate,
  type WorkflowTemplateDetail,
} from "./workflowTemplates";

const createPayload: WorkflowTemplateCreate = {
  name: "Sales cleanup",
  description: "Reusable rules",
  selected_rules: ["trim_whitespace", "remove_empty_rows"],
  source_filename: "messy.csv",
};

const templateDetail: WorkflowTemplateDetail = {
  id: 1,
  name: "Sales cleanup",
  description: "Reusable rules",
  selected_rules_count: 2,
  selected_rules: ["trim_whitespace", "remove_empty_rows"],
  source_session_id: null,
  source_filename: "messy.csv",
  created_at: "2026-07-15T00:00:00Z",
  updated_at: "2026-07-15T00:00:00Z",
  storage_note: "Templates store cleaning rules and metadata only.",
  new_upload_required_note: "Upload a new file before applying this template.",
};

describe("workflow templates client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("creates a workflow template", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => templateDetail });
    vi.stubGlobal("fetch", fetchMock);

    const result = await createTemplate(createPayload, "http://api.test");

    expect(result.id).toBe(1);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/templates",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(createPayload),
      }),
    );
  });

  it("lists workflow templates", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ templates: [templateDetail], total_count: 1 }),
    }));

    const result = await listTemplates("http://api.test");

    expect(result.total_count).toBe(1);
    expect(result.templates[0].name).toBe("Sales cleanup");
  });

  it("gets workflow template detail", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => templateDetail });
    vi.stubGlobal("fetch", fetchMock);

    const result = await getTemplate(1, "http://api.test");

    expect(result.selected_rules).toEqual(["trim_whitespace", "remove_empty_rows"]);
    expect(fetchMock).toHaveBeenCalledWith("http://api.test/templates/1", undefined);
  });

  it("updates workflow template metadata and rules", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => templateDetail });
    vi.stubGlobal("fetch", fetchMock);

    await updateTemplate(1, { name: "Updated", selected_rules: ["drop_empty_columns"] }, "http://api.test");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/templates/1",
      expect.objectContaining({
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "Updated", selected_rules: ["drop_empty_columns"] }),
      }),
    );
  });

  it("deletes workflow template", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal("fetch", fetchMock);

    await deleteTemplate(1, "http://api.test");

    expect(fetchMock).toHaveBeenCalledWith("http://api.test/templates/1", { method: "DELETE" });
  });

  it("creates workflow template from saved session", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => templateDetail });
    vi.stubGlobal("fetch", fetchMock);

    await createTemplateFromSession(7, createPayload, "http://api.test");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/templates/from-session/7",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("throws safe error for backend failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 404 }));

    await expect(getTemplate(404, "http://api.test")).rejects.toThrow(WorkflowTemplatesError);
  });

  it("throws safe error for unreadable responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => {
        throw new Error("bad json");
      },
    }));

    await expect(listTemplates("http://api.test")).rejects.toThrow(
      "Workflow templates returned an unreadable response.",
    );
  });
});
