from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt


class SupportedFileType(StrEnum):
    CSV = "csv"
    TSV = "tsv"
    TXT = "txt"
    XLSX = "xlsx"
    XLS = "xls"


class CleaningIssueSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class CleaningRuleType(StrEnum):
    TRIM_WHITESPACE = "trim_whitespace"
    REMOVE_EMPTY_ROWS = "remove_empty_rows"
    REMOVE_DUPLICATE_ROWS = "remove_duplicate_rows"
    DROP_EMPTY_COLUMNS = "drop_empty_columns"
    STANDARDIZE_COLUMN_NAMES = "standardize_column_names"
    PROMOTE_HEADER_ROW = "promote_header_row"
    GENERATE_MISSING_COLUMN_NAMES = "generate_missing_column_names"
    NORMALIZE_TEXT_CASING = "normalize_text_casing"
    CONVERT_NUMERIC_COLUMNS = "convert_numeric_columns"
    CONVERT_DATE_COLUMNS = "convert_date_columns"


class UploadedFileMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(min_length=1, max_length=255)
    file_type: SupportedFileType
    size_bytes: NonNegativeInt
    content_type: str | None = Field(default=None, max_length=120)
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class FileValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_valid: bool
    file_type: SupportedFileType | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class TablePreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: list[str]
    rows: list[dict[str, Any]]
    row_count_sampled: NonNegativeInt
    total_rows_estimate: NonNegativeInt | None = None
    truncated: bool = False


class DetectedStructure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delimiter: str | None = Field(default=None, max_length=8)
    sheet_names: list[str] = Field(default_factory=list)
    selected_sheet: str | None = None
    header_row_index: NonNegativeInt | None = None
    column_count: NonNegativeInt
    row_count_estimate: NonNegativeInt | None = None
    has_consistent_row_width: bool | None = None


class CleaningIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=500)
    severity: CleaningIssueSeverity = CleaningIssueSeverity.WARNING
    column_name: str | None = None
    row_index: NonNegativeInt | None = None
    affected_count: NonNegativeInt | None = None


class CleaningRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_type: CleaningRuleType
    enabled: bool = True
    parameters: dict[str, Any] = Field(default_factory=dict)


class CleaningSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules_applied: list[CleaningRuleType] = Field(default_factory=list)
    issues_detected: NonNegativeInt = 0
    rows_before: NonNegativeInt | None = None
    rows_after: NonNegativeInt | None = None
    columns_before: NonNegativeInt | None = None
    columns_after: NonNegativeInt | None = None


class CleaningSession(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: UUID = Field(default_factory=uuid4)
    uploaded_file: UploadedFileMetadata
    validation: FileValidationResult
    detected_structure: DetectedStructure | None = None
    raw_preview: TablePreview | None = None
    detected_issues: list[CleaningIssue] = Field(default_factory=list)
    selected_rules: list[CleaningRule] = Field(default_factory=list)
    summary: CleaningSummary | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    schema_version: PositiveInt = 1
