import { afterEach, describe, expect, it, vi } from "vitest";

import {
  StructureDetectionError,
  detectFileStructure,
  type StructureDetectionResult,
} from "./structureDetection";

const detectedResponse: StructureDetectionResult = {
  original_filename: "sales.csv",
  safe_filename: "sales.csv",
  detected_extension: "csv",
  file_size_bytes: 24,
  content_type: "text/csv",
  structure_status: "detected",
  delimiter: {
    detected_delimiter: ",",
    delimiter_label: "comma",
    delimiter_confidence: "high",
    detection_reason: "Comma produced the most consistent sampled row widths.",
  },
  workbook: null,
  selected_sheet_name: null,
  has_detected_header: true,
  header_row_index: 0,
  column_names: ["name", "amount"],
  generated_column_names: false,
  detected_column_count: 2,
  sampled_row_count: 2,
  preview_row_count: 1,
  total_row_count_calculated: false,
  total_row_count: null,
  warnings: [],
  preview: {
    columns: ["name", "amount"],
    rows: [["Ari", "1200"]],
  },
  next_step: "quality_issue_detection",
};

describe("detectFileStructure", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("posts multipart file data to the structure detection endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => detectedResponse,
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await detectFileStructure(
      new File(["name,amount\nAri,1200\n"], "sales.csv", { type: "text/csv" }),
      undefined,
      "http://api.test",
    );

    expect(result).toEqual(detectedResponse);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/files/detect-structure",
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      }),
    );
  });

  it("includes selected sheet name when provided", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ...detectedResponse, selected_sheet_name: "Sales" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await detectFileStructure(
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
      detectFileStructure(new File(["data"], "sales.csv"), undefined, "http://api.test"),
    ).rejects.toThrow(StructureDetectionError);
  });

  it("throws a safe error when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    await expect(
      detectFileStructure(new File(["data"], "sales.csv"), undefined, "http://api.test"),
    ).rejects.toThrow("Structure detection failed");
  });
});
