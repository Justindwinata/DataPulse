from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from datapulse_api.models.cleaning import SupportedFileType


class UploadValidationStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class UploadNextStep(StrEnum):
    STRUCTURE_DETECTION = "structure_detection"
    UPLOAD_SUPPORTED_FILE = "upload_supported_file"


class FileUploadValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_filename: str = Field(min_length=1, max_length=255)
    safe_filename: str = Field(min_length=1, max_length=255)
    detected_extension: str = Field(min_length=1, max_length=16)
    content_type: str | None = Field(default=None, max_length=120)
    file_size_bytes: NonNegativeInt
    max_size_bytes: NonNegativeInt
    is_supported: bool
    validation_status: UploadValidationStatus
    validation_messages: list[str] = Field(min_length=1)
    next_step: UploadNextStep
    structure_detection_available: bool = False


SUPPORTED_UPLOAD_FILE_TYPES: tuple[SupportedFileType, ...] = (
    SupportedFileType.CSV,
    SupportedFileType.TSV,
    SupportedFileType.TXT,
    SupportedFileType.XLSX,
    SupportedFileType.XLS,
)

SUPPORTED_UPLOAD_EXTENSIONS = frozenset(file_type.value for file_type in SUPPORTED_UPLOAD_FILE_TYPES)
