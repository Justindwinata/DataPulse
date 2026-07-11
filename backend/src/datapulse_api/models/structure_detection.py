from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt


class StructureDetectionStatus(StrEnum):
    DETECTED = "detected"
    REJECTED = "rejected"
    NOT_IMPLEMENTED = "not_implemented"


class DelimiterConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class StructureWarningSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class StructureNextStep(StrEnum):
    QUALITY_ISSUE_DETECTION = "quality_issue_detection"
    UPLOAD_SUPPORTED_FILE = "upload_supported_file"
    WAIT_FOR_EXCEL_SUPPORT = "wait_for_excel_support"


class DelimiterDetection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detected_delimiter: str | None = Field(default=None, max_length=4)
    delimiter_label: str = Field(min_length=1, max_length=32)
    delimiter_confidence: DelimiterConfidence
    detection_reason: str = Field(min_length=1, max_length=240)


class StructureWarning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=500)
    severity: StructureWarningSeverity = StructureWarningSeverity.WARNING


class RawTablePreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: list[str] = Field(min_length=1)
    rows: list[list[str]] = Field(default_factory=list)


class StructureDetectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_filename: str = Field(min_length=1, max_length=255)
    safe_filename: str = Field(min_length=1, max_length=255)
    detected_extension: str = Field(min_length=1, max_length=16)
    file_size_bytes: NonNegativeInt
    content_type: str | None = Field(default=None, max_length=120)
    structure_status: StructureDetectionStatus
    delimiter: DelimiterDetection | None = None
    has_detected_header: bool = False
    header_row_index: NonNegativeInt | None = None
    column_names: list[str] = Field(default_factory=list)
    generated_column_names: bool = False
    detected_column_count: NonNegativeInt = 0
    sampled_row_count: NonNegativeInt = 0
    preview_row_count: NonNegativeInt = 0
    total_row_count_calculated: bool = False
    total_row_count: NonNegativeInt | None = None
    warnings: list[StructureWarning] = Field(default_factory=list)
    preview: RawTablePreview | None = None
    next_step: StructureNextStep
