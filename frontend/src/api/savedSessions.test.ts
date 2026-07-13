import { afterEach, describe, expect, it, vi } from "vitest";

import {
  SavedSessionsError,
  createSession,
  deleteSession,
  getSession,
  listSessions,
  type SavedCleaningSessionCreate,
  type SavedCleaningSessionDetail,
} from "./savedSessions";

const createPayload: SavedCleaningSessionCreate = {
  source_filename: "messy.csv",
  detected_extension: "csv",
  content_type: "text/csv",
  file_size_bytes: 42,
  selected_sheet_name: null,
  structure_summary: { detected_column_count: 2 },
  quality_summary: { quality_score: 91, total_issue_count: 2 },
  selected_rules: ["trim_whitespace"],
  cleaning_summary: {
    before_summary: { row_count: 3, column_count: 2 },
    after_summary: { row_count: 2, column_count: 2 },
  },
  rule_effects: [{ rule: "trim_whitespace", status: "applied" }],
  export_summary: { format: "CSV" },
  report_summary: { format: "HTML" },
  preview_snapshot: { columns: ["name"], rows: [["Ari"]] },
};

const detail: SavedCleaningSessionDetail = {
  id: 1,
  source_filename: "messy.csv",
  detected_extension: "csv",
  selected_sheet_name: null,
  quality_score: 91,
  total_issue_count: 2,
  selected_rules_count: 1,
  rows_before: 3,
  rows_after: 2,
  columns_before: 2,
  columns_after: 2,
  created_at: "2026-07-14T00:00:00Z",
  updated_at: "2026-07-14T00:00:00Z",
  content_type: "text/csv",
  file_size_bytes: 42,
  structure_summary: { detected_column_count: 2 },
  quality_summary: { quality_score: 91 },
  selected_rules: ["trim_whitespace"],
  cleaning_summary: createPayload.cleaning_summary,
  rule_effects: createPayload.rule_effects,
  export_summary: createPayload.export_summary,
  report_summary: createPayload.report_summary,
  preview_snapshot: createPayload.preview_snapshot ?? null,
  storage_note: "Original uploaded files are not stored.",
};

describe("saved sessions client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("creates a saved session with JSON metadata", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => detail,
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await createSession(createPayload, "http://api.test");

    expect(result.id).toBe(1);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/sessions",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(createPayload),
      }),
    );
  });

  it("lists saved sessions", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ sessions: [detail], total_count: 1 }),
    }));

    const result = await listSessions("http://api.test");

    expect(result.total_count).toBe(1);
    expect(result.sessions[0].source_filename).toBe("messy.csv");
  });

  it("gets a saved session detail", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => detail,
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await getSession(1, "http://api.test");

    expect(result.storage_note).toContain("Original uploaded files");
    expect(fetchMock).toHaveBeenCalledWith("http://api.test/sessions/1", undefined);
  });

  it("deletes a saved session", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal("fetch", fetchMock);

    await deleteSession(1, "http://api.test");

    expect(fetchMock).toHaveBeenCalledWith("http://api.test/sessions/1", { method: "DELETE" });
  });

  it("throws a safe error when the backend returns an error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 404 }));

    await expect(getSession(404, "http://api.test")).rejects.toThrow(SavedSessionsError);
  });

  it("throws a safe error when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    await expect(listSessions("http://api.test")).rejects.toThrow("Saved sessions request failed");
  });
});
