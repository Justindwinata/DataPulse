from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

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
