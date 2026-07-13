from datetime import UTC, datetime

from datapulse_api.models import SavedCleaningSessionDetail
from datapulse_api.services.saved_session_report import (
    SAVED_REPORT_NOTICE,
    build_saved_session_report,
)


def make_saved_session() -> SavedCleaningSessionDetail:
    created_at = datetime(2026, 7, 14, 10, 0, tzinfo=UTC)
    return SavedCleaningSessionDetail(
        id=7,
        source_filename="messy.csv",
        detected_extension="csv",
        selected_sheet_name=None,
        quality_score=84,
        total_issue_count=3,
        selected_rules_count=2,
        rows_before=5,
        rows_after=4,
        columns_before=3,
        columns_after=2,
        created_at=created_at,
        updated_at=created_at,
        content_type="text/csv",
        file_size_bytes=120,
        structure_summary={
            "detected_column_count": 3,
            "delimiter_label": "comma",
            "warnings": [{"code": "duplicate_column_names", "message": "Duplicate headers."}],
        },
        quality_summary={
            "quality_score": 84,
            "total_issue_count": 3,
            "severity_counts": {"critical": 0, "warning": 2, "info": 1},
            "issues": [{"title": "Whitespace", "message": "Some cells need trimming."}],
        },
        selected_rules=["trim_whitespace", "drop_empty_columns"],
        cleaning_summary={
            "before_summary": {"row_count": 5, "column_count": 3},
            "after_summary": {"row_count": 4, "column_count": 2},
        },
        rule_effects=[
            {
                "rule": "trim_whitespace",
                "status": "applied",
                "message": "Trimmed whitespace.",
            }
        ],
        export_summary={"format": "CSV", "filename": "messy_cleaned.csv"},
        report_summary={"format": "HTML"},
        preview_snapshot={"columns": ["name"], "rows": [["Ari"]]},
    )


def test_build_saved_session_report_from_metadata() -> None:
    report = build_saved_session_report(make_saved_session())

    assert report.metadata.session_id == 7
    assert report.metadata.source_filename == "messy.csv"
    assert report.metadata_notice == SAVED_REPORT_NOTICE
    assert report.quality_score == 84
    assert report.total_issue_count == 3
    assert report.selected_rules == ["trim_whitespace", "drop_empty_columns"]
    assert report.rows_before == 5
    assert report.rows_after == 4
    assert report.columns_before == 3
    assert report.columns_after == 2
    assert report.preview_snapshot == {"columns": ["name"], "rows": [["Ari"]]}


def test_saved_session_report_states_metadata_limitations() -> None:
    report = build_saved_session_report(make_saved_session())

    assert "Original uploaded files are not stored by DataPulse." in report.metadata_notice
    assert any("stored metadata only" in limitation for limitation in report.limitations)
    assert any("cannot reprocess the original file" in limitation for limitation in report.limitations)
    assert any("local SQLite only" in limitation for limitation in report.limitations)
