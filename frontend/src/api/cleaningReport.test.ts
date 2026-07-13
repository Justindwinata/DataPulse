import { afterEach, describe, expect, it, vi } from "vitest";

import { CleaningReportError, generateCleaningReport } from "./cleaningReport";

describe("generateCleaningReport", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("posts multipart file data and selected rules to the report endpoint", async () => {
    const blob = new Blob(["<html></html>"], { type: "text/html" });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => blob,
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await generateCleaningReport(
      new File(["name\n Ari \n"], "messy.csv", { type: "text/csv" }),
      ["trim_whitespace"],
      undefined,
      "http://api.test",
    );

    expect(result).toBe(blob);
    const body = fetchMock.mock.calls[0][1].body as FormData;
    expect(body.get("rules")).toBe(JSON.stringify(["trim_whitespace"]));
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/files/cleaning-report.html",
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      }),
    );
  });

  it("includes selected sheet name when provided", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(["<html></html>"]),
    });
    vi.stubGlobal("fetch", fetchMock);

    await generateCleaningReport(
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
      generateCleaningReport(new File(["data"], "messy.csv"), [], undefined, "http://api.test"),
    ).rejects.toThrow(CleaningReportError);
  });

  it("throws a safe error when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    await expect(
      generateCleaningReport(new File(["data"], "messy.csv"), [], undefined, "http://api.test"),
    ).rejects.toThrow("HTML cleaning report generation failed");
  });
});
