from datetime import UTC, datetime

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from datapulse_api.models.cleaning import CleaningPreviewResult, CleaningRuleCode
from datapulse_api.models.quality import DataQualityResult
from datapulse_api.models.structure_detection import StructureDetectionResult


class ReportExportMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_format: str = "CSV"
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=120)
    csv_first_strategy: bool = True
    original_file_modified: bool = False


class CleaningReportMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = "DataPulse Cleaning Report"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_filename: str = Field(min_length=1, max_length=255)
    detected_extension: str = Field(min_length=1, max_length=16)
    selected_sheet_name: str | None = Field(default=None, max_length=255)
    selected_rules: list[CleaningRuleCode] = Field(default_factory=list)


class CleaningReportDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: CleaningReportMetadata
    structure: StructureDetectionResult
    quality: DataQualityResult
    cleaning: CleaningPreviewResult
    export: ReportExportMetadata
    limitations: list[str] = Field(default_factory=list)


class SavedSessionReportMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = "DataPulse Saved Cleaning Session Report"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: int
    source_filename: str = Field(min_length=1, max_length=255)
    detected_extension: str = Field(min_length=1, max_length=16)
    selected_sheet_name: str | None = Field(default=None, max_length=255)
    session_created_at: datetime
    session_updated_at: datetime


class SavedSessionReportDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: SavedSessionReportMetadata
    metadata_notice: str
    quality_score: int | None = Field(default=None, ge=0, le=100)
    total_issue_count: NonNegativeInt = 0
    selected_rules: list[str] = Field(default_factory=list)
    rows_before: NonNegativeInt | None = None
    rows_after: NonNegativeInt | None = None
    columns_before: NonNegativeInt | None = None
    columns_after: NonNegativeInt | None = None
    export_format: str = "CSV"
    structure_summary: dict[str, Any] = Field(default_factory=dict)
    quality_summary: dict[str, Any] = Field(default_factory=dict)
    cleaning_summary: dict[str, Any] = Field(default_factory=dict)
    rule_effects: list[dict[str, Any]] = Field(default_factory=list)
    export_summary: dict[str, Any] = Field(default_factory=dict)
    report_summary: dict[str, Any] = Field(default_factory=dict)
    preview_snapshot: dict[str, Any] | None = None
    limitations: list[str] = Field(default_factory=list)
