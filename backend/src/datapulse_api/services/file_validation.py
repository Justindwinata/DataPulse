from pathlib import PurePath

from datapulse_api.models import (
    SUPPORTED_UPLOAD_EXTENSIONS,
    FileUploadValidationResponse,
    UploadNextStep,
    UploadValidationStatus,
)

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
SUPPORTED_FORMATS_LABEL = "CSV, TSV, TXT, XLSX, and XLS"


def sanitize_filename(filename: str) -> str:
    basename = PurePath(filename.replace("\\", "/")).name.strip()
    return basename or "uploaded_file"


def detect_extension(filename: str) -> str:
    safe_filename = sanitize_filename(filename)
    if "." not in safe_filename:
        return ""
    return safe_filename.rsplit(".", maxsplit=1)[1].lower()


def validate_uploaded_file_metadata(
    *,
    filename: str,
    content_type: str | None,
    file_size_bytes: int,
    max_size_bytes: int = MAX_UPLOAD_SIZE_BYTES,
) -> FileUploadValidationResponse:
    safe_filename = sanitize_filename(filename)
    detected_extension = detect_extension(safe_filename)
    messages: list[str] = []

    extension_supported = detected_extension in SUPPORTED_UPLOAD_EXTENSIONS
    size_valid = 0 < file_size_bytes <= max_size_bytes

    if extension_supported:
        messages.append("File extension is supported.")
    else:
        messages.append(
            f"Unsupported file extension. Supported formats are {SUPPORTED_FORMATS_LABEL}."
        )

    if file_size_bytes == 0:
        messages.append("File is empty. Upload a non-empty tabular file.")
    elif file_size_bytes > max_size_bytes:
        messages.append("File size exceeds the 10 MB limit.")
    else:
        messages.append("File size is within the 10 MB limit.")

    is_supported = extension_supported and size_valid
    validation_status = (
        UploadValidationStatus.ACCEPTED if is_supported else UploadValidationStatus.REJECTED
    )
    next_step = (
        UploadNextStep.STRUCTURE_DETECTION
        if is_supported
        else UploadNextStep.UPLOAD_SUPPORTED_FILE
    )

    return FileUploadValidationResponse(
        original_filename=filename,
        safe_filename=safe_filename,
        detected_extension=detected_extension or "unknown",
        content_type=content_type,
        file_size_bytes=max(file_size_bytes, 0),
        max_size_bytes=max_size_bytes,
        is_supported=is_supported,
        validation_status=validation_status,
        validation_messages=messages,
        next_step=next_step,
        structure_detection_available=False,
    )
