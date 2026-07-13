import { afterEach, describe, expect, it, vi } from "vitest";

import {
  CleanedCsvExportError,
  exportCleanedCsv,
  filenameFromContentDisposition,
} from "./cleanedCsvExport";

describe("exportCleanedCsv", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("posts multipart file data and selected rules to the export endpoint", async () => {
    const blob = new Blob(["name\nAri\n"], { type: "text/csv" });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => blob,
      headers: new Headers({
        "content-disposition": 'attachment; filename="messy_cleaned.csv"',
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await exportCleanedCsv(
      new File(["name\n Ari \n"], "messy.csv", { type: "text/csv" }),
      ["trim_whitespace"],
      undefined,
      "http://api.test",
    );

    expect(result.blob).toBe(blob);
    expect(result.filename).toBe("messy_cleaned.csv");
    const body = fetchMock.mock.calls[0][1].body as FormData;
    expect(body.get("rules")).toBe(JSON.stringify(["trim_whitespace"]));
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/files/export-cleaned-csv",
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      }),
    );
  });

  it("includes selected sheet name when provided", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(["name\nAri\n"]),
      headers: new Headers(),
    });
    vi.stubGlobal("fetch", fetchMock);

    await exportCleanedCsv(
      new File(["workbook"], "workbook.xlsx"),
      ["trim_whitespace"],
      "Sales",
      "http://api.test",
    );

    const body = fetchMock.mock.calls[0][1].body as FormData;
    expect(body.get("sheet_name")).toBe("Sales");
  });

  it("throws a safe error when the backend returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 400 }));

    await expect(
      exportCleanedCsv(new File(["data"], "messy.csv"), [], undefined, "http://api.test"),
    ).rejects.toThrow(CleanedCsvExportError);
  });

  it("throws a safe error when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    await expect(
      exportCleanedCsv(new File(["data"], "messy.csv"), [], undefined, "http://api.test"),
    ).rejects.toThrow("Cleaned CSV export failed");
  });
});

describe("filenameFromContentDisposition", () => {
  it("extracts quoted filenames", () => {
    expect(filenameFromContentDisposition('attachment; filename="sales_cleaned.csv"')).toBe(
      "sales_cleaned.csv",
    );
  });

  it("returns a safe default when the header is missing", () => {
    expect(filenameFromContentDisposition(null)).toBe("datapulse_cleaned.csv");
  });
});
