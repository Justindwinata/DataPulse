import pytest
from pydantic import ValidationError

from datapulse_api.models import (
    CleanedTablePreview,
    CleaningNextStep,
    CleaningPreviewResult,
    CleaningRuleCode,
    CleaningRuleEffect,
    CleaningRuleEffectStatus,
    CleaningStatus,
    CleaningSummaryAfter,
    CleaningSummaryBefore,
)


def test_cleaning_rule_code_values_are_stable_api_contracts() -> None:
    assert [rule.value for rule in CleaningRuleCode] == [
        "trim_whitespace",
        "normalize_missing_tokens",
        "clean_numeric_values",
        "clean_date_values",
        "standardize_category_text",
        "recalculate_line_totals",
        "remove_empty_rows",
        "remove_duplicate_rows",
        "drop_empty_columns",
        "standardize_column_names",
        "generate_missing_column_names",
    ]


def test_cleaning_status_values_are_stable_api_contracts() -> None:
    assert [status.value for status in CleaningStatus] == [
        "preview_generated",
        "rejected",
        "sheet_selection_required",
    ]


def test_cleaning_preview_result_accepts_preview_shape() -> None:
    result = CleaningPreviewResult(
        cleaning_status=CleaningStatus.PREVIEW_GENERATED,
        original_filename="messy.csv",
        safe_filename="messy.csv",
        detected_extension="csv",
        applied_rules=[CleaningRuleCode.TRIM_WHITESPACE],
        before_summary=CleaningSummaryBefore(
            row_count=2,
            column_count=2,
            empty_rows_count=0,
            duplicate_rows_count=0,
            empty_columns_count=0,
        ),
        after_summary=CleaningSummaryAfter(
            row_count=2,
            column_count=2,
            removed_empty_rows_count=0,
            removed_duplicate_rows_count=0,
            dropped_empty_columns_count=0,
            renamed_columns_count=0,
        ),
        rule_effects=[
            CleaningRuleEffect(
                rule=CleaningRuleCode.TRIM_WHITESPACE,
                label="Trim whitespace",
                status=CleaningRuleEffectStatus.APPLIED,
                message="Trimmed whitespace in sampled cells.",
                affected_rows=1,
                affected_columns=1,
            )
        ],
        cleaned_preview=CleanedTablePreview(
            columns=["name", "amount"],
            rows=[["Ari", "1200"]],
        ),
        next_step=CleaningNextStep.DOWNLOAD_CLEANED_CSV,
    )

    assert result.cleaning_status == CleaningStatus.PREVIEW_GENERATED
    assert result.rule_effects[0].status == CleaningRuleEffectStatus.APPLIED
    assert result.cleaned_preview.rows == [["Ari", "1200"]]


def test_cleaning_preview_rejects_invalid_negative_summary_counts() -> None:
    with pytest.raises(ValidationError):
        CleaningSummaryBefore(row_count=-1, column_count=2)
