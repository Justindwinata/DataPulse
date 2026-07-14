from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt


JsonObject = dict[str, Any]


class SavedCleaningSessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_filename: str = Field(min_length=1, max_length=255)
    detected_extension: str = Field(min_length=1, max_length=16)
    content_type: str | None = Field(default=None, max_length=120)
    file_size_bytes: NonNegativeInt
    selected_sheet_name: str | None = Field(default=None, max_length=255)
    structure_summary: JsonObject
    quality_summary: JsonObject
    selected_rules: list[str] = Field(min_length=1)
    cleaning_summary: JsonObject
    rule_effects: list[JsonObject] = Field(default_factory=list)
    export_summary: JsonObject
    report_summary: JsonObject = Field(default_factory=dict)
    preview_snapshot: JsonObject | None = None


class SavedCleaningSessionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    source_filename: str
    detected_extension: str
    selected_sheet_name: str | None = None
    quality_score: int | None = Field(default=None, ge=0, le=100)
    total_issue_count: NonNegativeInt = 0
    selected_rules_count: NonNegativeInt = 0
    rows_before: NonNegativeInt | None = None
    rows_after: NonNegativeInt | None = None
    columns_before: NonNegativeInt | None = None
    columns_after: NonNegativeInt | None = None
    created_at: datetime
    updated_at: datetime


class SavedCleaningSessionDetail(SavedCleaningSessionSummary):
    content_type: str | None = None
    file_size_bytes: NonNegativeInt
    structure_summary: JsonObject
    quality_summary: JsonObject
    selected_rules: list[str]
    cleaning_summary: JsonObject
    rule_effects: list[JsonObject] = Field(default_factory=list)
    export_summary: JsonObject
    report_summary: JsonObject = Field(default_factory=dict)
    preview_snapshot: JsonObject | None = None
    storage_note: str = "Original uploaded files are not stored. History stores metadata and summaries only."


class SavedCleaningSessionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sessions: list[SavedCleaningSessionSummary] = Field(default_factory=list)
    total_count: NonNegativeInt = 0


class SavedCleaningRuleSetResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: int
    source_filename: str
    selected_rules: list[str]
    selected_rules_count: NonNegativeInt
    created_at: datetime
    original_file_storage_note: str = "Original uploaded files are not stored by DataPulse."
    new_upload_required_note: str = "Upload a new file before applying these restored cleaning rules."


def utc_now() -> datetime:
    return datetime.now(UTC)
