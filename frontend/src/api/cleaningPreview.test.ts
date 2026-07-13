import { afterEach, describe, expect, it, vi } from "vitest";

import {
  CleaningPreviewError,
  generateCleaningPreview,
  type CleaningPreviewResult,
} from "./cleaningPreview";

const previewResponse: CleaningPreviewResult = {
  cleaning_status: "preview_generated",
  original_filename: "messy.csv",
  safe_filename: "messy.csv",
  detected_extension: "csv",
  selected_sheet_name: null,
  applied_rules: ["trim_whitespace"],
  before_summary: {
    row_count: 1,
    column_count: 2,
    empty_rows_count: 0,
    duplicate_rows_count: 0,
    empty_columns_count: 0,
  },
  after_summary: {
    row_count: 1,
    column_count: 2,
    removed_empty_rows_count: 0,
    removed_duplicate_rows_count: 0,
    dropped_empty_columns_count: 0,
    renamed_columns_count: 0,
  },
  rule_effects: [
    {
      rule: "trim_whitespace",
      label: "Trim whitespace",
      status: "applied",
      message: "Trimmed whitespace in 1 sampled cells.",
      affected_rows: 1,
      affected_columns: 1,
    },
  ],
  cleaned_preview: {
    columns: ["name", "amount"],
    rows: [["Ari", "1200"]],
  },
  warnings: [
    {
      code: "sample_based_preview",
      message: "Cleaning preview is generated from a bounded sample.",
      severity: "info",
    },
  ],
  next_step: "download_cleaned_csv",
};

describe("generateCleaningPreview", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("posts multipart file data and selected rules to the cleaning preview endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => previewResponse,
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await generateCleaningPreview(
      new File(["name,amount\n Ari ,1200\n"], "messy.csv", { type: "text/csv" }),
      ["trim_whitespace"],
      undefined,
      "http://api.test",
    );

    expect(result).toEqual(previewResponse);
    const body = fetchMock.mock.calls[0][1].body as FormData;
    expect(body.get("rules")).toBe(JSON.stringify(["trim_whitespace"]));
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/files/apply-cleaning-preview",
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      }),
    );
  });

  it("includes selected sheet name when provided", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ...previewResponse, selected_sheet_name: "Sales" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await generateCleaningPreview(
      new File(["workbook"], "workbook.xlsx"),
      ["trim_whitespace"],
      "Sales",
      "http://api.test",
    );

    const body = fetchMock.mock.calls[0][1].body as FormData;
    expect(body.get("sheet_name")).toBe("Sales");
  });

  it("throws a safe error when the backend returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));

    await expect(
      generateCleaningPreview(
        new File(["data"], "messy.csv"),
        ["trim_whitespace"],
        undefined,
        "http://api.test",
      ),
    ).rejects.toThrow(CleaningPreviewError);
  });

  it("throws a safe error when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    await expect(
      generateCleaningPreview(
        new File(["data"], "messy.csv"),
        ["trim_whitespace"],
        undefined,
        "http://api.test",
      ),
    ).rejects.toThrow("Cleaning preview failed");
  });
});
