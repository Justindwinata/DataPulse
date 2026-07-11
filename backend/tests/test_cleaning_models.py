from uuid import UUID

import pytest
from pydantic import ValidationError

from datapulse_api.models import (
    CleaningIssue,
    CleaningIssueSeverity,
    CleaningRule,
    CleaningRuleType,
    CleaningSession,
    CleaningSummary,
    DetectedStructure,
    FileValidationResult,
    SupportedFileType,
    TablePreview,
    UploadedFileMetadata,
)


def test_supported_file_type_values_match_planned_formats() -> None:
    assert [file_type.value for file_type in SupportedFileType] == [
        "csv",
        "tsv",
        "txt",
        "xlsx",
        "xls",
    ]


def test_cleaning_rule_type_values_are_deterministic_actions() -> None:
    assert CleaningRuleType.TRIM_WHITESPACE.value == "trim_whitespace"
    assert CleaningRuleType.REMOVE_DUPLICATE_ROWS.value == "remove_duplicate_rows"
    assert CleaningRuleType.CONVERT_DATE_COLUMNS.value == "convert_date_columns"


def test_uploaded_file_metadata_rejects_negative_size() -> None:
    with pytest.raises(ValidationError):
        UploadedFileMetadata(
            filename="messy.csv",
            file_type=SupportedFileType.CSV,
            size_bytes=-1,
        )


def test_cleaning_session_can_represent_foundation_workflow_state() -> None:
    uploaded_file = UploadedFileMetadata(
        filename="messy.csv",
        file_type=SupportedFileType.CSV,
        size_bytes=2048,
        content_type="text/csv",
    )
    validation = FileValidationResult(is_valid=True, file_type=SupportedFileType.CSV)
    detected_structure = DetectedStructure(
        delimiter=",",
        header_row_index=0,
        column_count=3,
        row_count_estimate=25,
        has_consistent_row_width=True,
    )
    preview = TablePreview(
        columns=["name", "email", "signup_date"],
        rows=[{"name": " Ada ", "email": "ada@example.com", "signup_date": "2026-07-12"}],
        row_count_sampled=1,
        total_rows_estimate=25,
    )
    issue = CleaningIssue(
        code="whitespace_detected",
        message="Leading or trailing whitespace was detected.",
        severity=CleaningIssueSeverity.INFO,
        affected_count=1,
    )
    rule = CleaningRule(rule_type=CleaningRuleType.TRIM_WHITESPACE)
    summary = CleaningSummary(
        rules_applied=[CleaningRuleType.TRIM_WHITESPACE],
        issues_detected=1,
        rows_before=25,
        rows_after=25,
        columns_before=3,
        columns_after=3,
    )

    session = CleaningSession(
        uploaded_file=uploaded_file,
        validation=validation,
        detected_structure=detected_structure,
        raw_preview=preview,
        detected_issues=[issue],
        selected_rules=[rule],
        summary=summary,
    )

    assert isinstance(session.session_id, UUID)
    assert session.uploaded_file.filename == "messy.csv"
    assert session.detected_structure is not None
    assert session.detected_structure.delimiter == ","
    assert session.selected_rules[0].rule_type == CleaningRuleType.TRIM_WHITESPACE
