import pytest
from pydantic import ValidationError

from datapulse_api.models import (
    SavedCleaningSessionCreate,
    SavedCleaningSessionDetail,
    SavedCleaningSessionListResponse,
)
from datapulse_api.models.sessions import utc_now


def valid_create_payload() -> dict:
    return {
        "source_filename": "messy.csv",
        "detected_extension": "csv",
        "content_type": "text/csv",
        "file_size_bytes": 42,
        "structure_summary": {"detected_column_count": 2},
        "quality_summary": {"quality_score": 91, "total_issue_count": 2},
        "selected_rules": ["trim_whitespace"],
        "cleaning_summary": {
            "before_summary": {"row_count": 3, "column_count": 2},
            "after_summary": {"row_count": 2, "column_count": 2},
        },
        "rule_effects": [{"rule": "trim_whitespace", "status": "applied"}],
        "export_summary": {"format": "CSV", "filename": "messy_cleaned.csv"},
        "report_summary": {"format": "HTML"},
        "preview_snapshot": {"columns": ["name"], "rows": [["Ari"]]},
    }


def test_saved_cleaning_session_create_accepts_metadata_only_payload() -> None:
    session = SavedCleaningSessionCreate(**valid_create_payload())

    assert session.source_filename == "messy.csv"
    assert session.selected_rules == ["trim_whitespace"]
    assert session.preview_snapshot == {"columns": ["name"], "rows": [["Ari"]]}


def test_saved_cleaning_session_create_requires_selected_rules() -> None:
    payload = valid_create_payload()
    payload["selected_rules"] = []

    with pytest.raises(ValidationError):
        SavedCleaningSessionCreate(**payload)


def test_saved_cleaning_session_detail_includes_storage_note() -> None:
    now = utc_now()
    detail = SavedCleaningSessionDetail(
        id=1,
        source_filename="messy.csv",
        detected_extension="csv",
        quality_score=91,
        total_issue_count=2,
        selected_rules_count=1,
        rows_before=3,
        rows_after=2,
        columns_before=2,
        columns_after=2,
        created_at=now,
        updated_at=now,
        content_type="text/csv",
        file_size_bytes=42,
        structure_summary={"detected_column_count": 2},
        quality_summary={"quality_score": 91},
        selected_rules=["trim_whitespace"],
        cleaning_summary={"after_summary": {"row_count": 2}},
        export_summary={"format": "CSV"},
    )

    assert "Original uploaded files are not stored" in detail.storage_note


def test_saved_cleaning_session_list_response_counts_sessions() -> None:
    response = SavedCleaningSessionListResponse(sessions=[], total_count=0)

    assert response.total_count == 0
