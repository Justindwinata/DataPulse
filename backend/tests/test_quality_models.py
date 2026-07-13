import pytest
from pydantic import ValidationError

from datapulse_api.models import (
    ColumnProfile,
    DataQualityIssue,
    DataQualityResult,
    InferredColumnType,
    IssueSeverity,
    QualityNextStep,
    QualityStatus,
    SeverityCounts,
)


def test_quality_status_values_are_stable_api_contracts() -> None:
    assert [status.value for status in QualityStatus] == [
        "profiled",
        "rejected",
        "sheet_selection_required",
    ]


def test_issue_severity_values_are_stable_api_contracts() -> None:
    assert [severity.value for severity in IssueSeverity] == [
        "info",
        "warning",
        "critical",
    ]


def test_inferred_column_type_values_are_stable_api_contracts() -> None:
    assert [column_type.value for column_type in InferredColumnType] == [
        "text",
        "number",
        "date",
        "boolean",
        "mixed",
        "empty",
    ]


def test_data_quality_result_accepts_profiled_shape() -> None:
    result = DataQualityResult(
        quality_status=QualityStatus.PROFILED,
        original_filename="messy_sales.csv",
        safe_filename="messy_sales.csv",
        detected_extension="csv",
        sampled_row_count=20,
        detected_column_count=2,
        total_issue_count=1,
        severity_counts=SeverityCounts(warning=1),
        quality_score=93,
        issues=[
            DataQualityIssue(
                code="missing_values",
                title="Missing values detected",
                message="Some columns contain empty values in the sampled data.",
                severity=IssueSeverity.WARNING,
                affected_columns=["amount"],
                affected_row_count=2,
            )
        ],
        columns=[
            ColumnProfile(
                column_name="amount",
                column_index=1,
                non_empty_count=18,
                missing_count=2,
                missing_percentage=10.0,
                inferred_type=InferredColumnType.NUMBER,
                unique_count=17,
                sample_values=["1200", "1500"],
                issues=["missing_values"],
            )
        ],
        next_step=QualityNextStep.CLEANING_RULES,
    )

    assert result.quality_status == QualityStatus.PROFILED
    assert result.severity_counts.warning == 1
    assert result.issues[0].suggested_cleaning_rule is None
    assert result.columns[0].inferred_type == InferredColumnType.NUMBER


def test_quality_score_must_stay_between_zero_and_one_hundred() -> None:
    with pytest.raises(ValidationError):
        DataQualityResult(
            quality_status=QualityStatus.PROFILED,
            original_filename="messy_sales.csv",
            safe_filename="messy_sales.csv",
            detected_extension="csv",
            quality_score=120,
            next_step=QualityNextStep.CLEANING_RULES,
        )
