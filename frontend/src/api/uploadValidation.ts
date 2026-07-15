export type UploadValidationStatus = "accepted" | "rejected";
export type UploadNextStep = "structure_detection" | "upload_supported_file";

export type FileUploadValidationResponse = {
  original_filename: string;
  safe_filename: string;
  detected_extension: string;
  content_type: string | null;
  file_size_bytes: number;
  max_size_bytes: number;
  is_supported: boolean;
  validation_status: UploadValidationStatus;
  validation_messages: string[];
  next_step: UploadNextStep;
  structure_detection_available: boolean;
};

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class UploadValidationError extends Error {
  constructor(message = "Upload validation failed. Confirm the backend is running and try again.") {
    super(message);
    this.name = "UploadValidationError";
  }
}

export async function validateUploadFile(
  file: File,
  apiBaseUrl: string = API_BASE_URL,
): Promise<FileUploadValidationResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}/files/validate-upload`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new UploadValidationError();
  }

  if (!response.ok) {
    throw new UploadValidationError(`Upload validation failed with status ${response.status}.`);
  }

  try {
    return (await response.json()) as FileUploadValidationResponse;
  } catch (error) {
    throw new UploadValidationError("Upload validation returned an unreadable response.");
  }
}
