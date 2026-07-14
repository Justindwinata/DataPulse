import pytest
from pydantic import ValidationError

from datapulse_api.models import (
    WorkflowTemplateCreate,
    WorkflowTemplateDetail,
    WorkflowTemplateListResponse,
    WorkflowTemplateUpdate,
)
from datapulse_api.models.templates import utc_now


def test_workflow_template_create_normalizes_name_and_description() -> None:
    template = WorkflowTemplateCreate(
        name="  Analyst cleanup  ",
        description="  Reusable sales export rules  ",
        selected_rules=["trim_whitespace", "remove_empty_rows"],
        source_session_id=3,
        source_filename="messy.csv",
    )

    assert template.name == "Analyst cleanup"
    assert template.description == "Reusable sales export rules"
    assert [rule.value for rule in template.selected_rules] == [
        "trim_whitespace",
        "remove_empty_rows",
    ]


def test_workflow_template_create_requires_non_empty_name() -> None:
    with pytest.raises(ValidationError):
        WorkflowTemplateCreate(name="   ", selected_rules=["trim_whitespace"])


def test_workflow_template_create_requires_selected_rules() -> None:
    with pytest.raises(ValidationError):
        WorkflowTemplateCreate(name="Cleanup", selected_rules=[])


def test_workflow_template_create_rejects_unsupported_rule_code() -> None:
    with pytest.raises(ValidationError):
        WorkflowTemplateCreate(name="Cleanup", selected_rules=["convert_numeric_columns"])


def test_workflow_template_update_accepts_partial_payload() -> None:
    update = WorkflowTemplateUpdate(description="  Updated note  ")

    assert update.name is None
    assert update.description == "Updated note"
    assert update.selected_rules is None


def test_workflow_template_detail_includes_metadata_only_notes() -> None:
    now = utc_now()
    detail = WorkflowTemplateDetail(
        id=1,
        name="Cleanup",
        description=None,
        selected_rules_count=1,
        selected_rules=["trim_whitespace"],
        source_session_id=None,
        source_filename=None,
        created_at=now,
        updated_at=now,
    )

    assert "Original files are not stored" in detail.storage_note
    assert "Upload a new file" in detail.new_upload_required_note


def test_workflow_template_list_response_counts_templates() -> None:
    response = WorkflowTemplateListResponse(templates=[], total_count=0)

    assert response.total_count == 0
