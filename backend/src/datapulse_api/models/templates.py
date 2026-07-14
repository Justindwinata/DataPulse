from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, field_validator

from datapulse_api.models.cleaning import CleaningRuleCode


class WorkflowTemplateCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    selected_rules: list[CleaningRuleCode] = Field(min_length=1)
    source_session_id: int | None = None
    source_filename: str | None = Field(default=None, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Template name is required.")
        return stripped

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class WorkflowTemplateUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    selected_rules: list[CleaningRuleCode] | None = Field(default=None, min_length=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("Template name is required.")
        return stripped

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class WorkflowTemplateSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    description: str | None = None
    selected_rules_count: NonNegativeInt
    source_session_id: int | None = None
    source_filename: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkflowTemplateDetail(WorkflowTemplateSummary):
    selected_rules: list[CleaningRuleCode]
    storage_note: str = "Templates store cleaning rules and metadata only. Original files are not stored."
    new_upload_required_note: str = "Upload a new file before applying this template."


class WorkflowTemplateListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    templates: list[WorkflowTemplateSummary] = Field(default_factory=list)
    total_count: NonNegativeInt = 0


def utc_now() -> datetime:
    return datetime.now(UTC)
