import { afterEach, describe, expect, it, vi } from "vitest";

import {
  DataQualityError,
  detectDataQuality,
  type DataQualityResult,
} from "./dataQuality";

const qualityResponse: DataQualityResult = {
  quality_status: "profiled",
  original_filename: "sales.csv",
  safe_filename: "sales.csv",
  detected_extension: "csv",
  selected_sheet_name: null,
  sampled_row_count: 2,
  detected_column_count: 2,
  total_issue_count: 1,
  severity_counts: {
    info: 0,
    warning: 1,
    critical: 0,
  },
  quality_score: 93,
  issues: [
    {
      code: "missing_values",
      title: "Missing values detected",
      message: "Some columns contain empty values in the sampled data.",
      severity: "warning",
      affected_columns: ["amount"],
      affected_row_count: 1,
      suggested_cleaning_rule: null,
    },
  ],
  columns: [
    {
      column_name: "amount",
      column_index: 1,
      non_empty_count: 1,
      missing_count: 1,
      missing_percentage: 50,
      inferred_type: "number",
      unique_count: 1,
      sample_values: ["1200"],
      issues: ["missing_values"],
    },
  ],
  messages: [],
  next_step: "cleaning_rules",
};

describe("detectDataQuality", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("posts multipart file data to the quality endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => qualityResponse,
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await detectDataQuality(
      new File(["name,amount\nAri,1200\n"], "sales.csv", { type: "text/csv" }),
      undefined,
      "http://api.test",
    );

    expect(result).toEqual(qualityResponse);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/files/detect-quality",
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      }),
    );
  });

  it("includes selected sheet name when provided", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ...qualityResponse, selected_sheet_name: "Sales" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await detectDataQuality(
      new File(["workbook"], "workbook.xlsx"),
      "Sales",
      "http://api.test",
    );

    const body = fetchMock.mock.calls[0][1].body as FormData;
    expect(body.get("sheet_name")).toBe("Sales");
  });

  it("throws a safe error when the backend returns an error status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
      }),
    );

    await expect(
      detectDataQuality(new File(["data"], "sales.csv"), undefined, "http://api.test"),
    ).rejects.toThrow(DataQualityError);
  });

  it("throws a safe error when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    await expect(
      detectDataQuality(new File(["data"], "sales.csv"), undefined, "http://api.test"),
    ).rejects.toThrow("Data quality analysis failed");
  });
});
