import { afterEach, describe, expect, it, vi } from "vitest";

import {
  UploadValidationError,
  validateUploadFile,
  type FileUploadValidationResponse,
} from "./uploadValidation";

const acceptedResponse: FileUploadValidationResponse = {
  original_filename: "messy.csv",
  safe_filename: "messy.csv",
  detected_extension: "csv",
  content_type: "text/csv",
  file_size_bytes: 18,
  max_size_bytes: 10 * 1024 * 1024,
  is_supported: true,
  validation_status: "accepted",
  validation_messages: ["File extension is supported.", "File size is within the 10 MB limit."],
  next_step: "structure_detection",
  structure_detection_available: false,
};

describe("validateUploadFile", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("posts multipart file data to the validation endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => acceptedResponse,
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await validateUploadFile(
      new File(["name,total\nAda,10\n"], "messy.csv", { type: "text/csv" }),
      "http://api.test",
    );

    expect(result).toEqual(acceptedResponse);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/files/validate-upload",
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      }),
    );
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
      validateUploadFile(new File(["data"], "messy.csv"), "http://api.test"),
    ).rejects.toThrow(UploadValidationError);
  });

  it("throws a safe error when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    await expect(
      validateUploadFile(new File(["data"], "messy.csv"), "http://api.test"),
    ).rejects.toThrow("Upload validation failed");
  });
});
