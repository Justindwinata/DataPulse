from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt


class QualityStatus(StrEnum):
    PROFILED = "profiled"
    REJECTED = "rejected"
    SHEET_SELECTION_REQUIRED = "sheet_selection_required"


class IssueSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class InferredColumnType(StrEnum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    MIXED = "mixed"
    EMPTY = "empty"


class QualityNextStep(StrEnum):
    CLEANING_RULES = "cleaning_rules"
    SELECT_EXCEL_SHEET = "select_excel_sheet"
    UPLOAD_SUPPORTED_FILE = "upload_supported_file"


class SeverityCounts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    info: NonNegativeInt = 0
    warning: NonNegativeInt = 0
    critical: NonNegativeInt = 0


class DataQualityIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=500)
    severity: IssueSeverity
    affected_columns: list[str] = Field(default_factory=list)
    affected_row_count: NonNegativeInt | None = None
    suggested_cleaning_rule: str | None = Field(default=None, max_length=80)


class ColumnProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_name: str = Field(min_length=1, max_length=255)
    column_index: NonNegativeInt
    non_empty_count: NonNegativeInt
    missing_count: NonNegativeInt
    missing_percentage: float = Field(ge=0, le=100)
    inferred_type: InferredColumnType
    unique_count: NonNegativeInt
    sample_values: list[str] = Field(default_factory=list, max_length=5)
    issues: list[str] = Field(default_factory=list)


class DataQualityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quality_status: QualityStatus
    original_filename: str = Field(min_length=1, max_length=255)
    safe_filename: str = Field(min_length=1, max_length=255)
    detected_extension: str = Field(min_length=1, max_length=16)
    selected_sheet_name: str | None = Field(default=None, max_length=255)
    sampled_row_count: NonNegativeInt = 0
    detected_column_count: NonNegativeInt = 0
    total_issue_count: NonNegativeInt = 0
    severity_counts: SeverityCounts = Field(default_factory=SeverityCounts)
    quality_score: int = Field(default=100, ge=0, le=100)
    issues: list[DataQualityIssue] = Field(default_factory=list)
    columns: list[ColumnProfile] = Field(default_factory=list)
    messages: list[str] = Field(default_factory=list)
    next_step: QualityNextStep
