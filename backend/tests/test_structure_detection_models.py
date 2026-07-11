import pytest
from pydantic import ValidationError

from datapulse_api.models import (
    DelimiterConfidence,
    DelimiterDetection,
    RawTablePreview,
    StructureDetectionResult,
    StructureDetectionStatus,
    StructureNextStep,
    StructureWarning,
    StructureWarningSeverity,
)


def test_structure_detection_status_values_are_stable_api_contracts() -> None:
    assert StructureDetectionStatus.DETECTED.value == "detected"
    assert StructureDetectionStatus.REJECTED.value == "rejected"
    assert StructureDetectionStatus.NOT_IMPLEMENTED.value == "not_implemented"


def test_delimiter_confidence_values_are_stable_api_contracts() -> None:
    assert [confidence.value for confidence in DelimiterConfidence] == [
        "high",
        "medium",
        "low",
        "unknown",
    ]


def test_structure_detection_result_accepts_detected_csv_shape() -> None:
    result = StructureDetectionResult(
        original_filename="messy_sales.csv",
        safe_filename="messy_sales.csv",
        detected_extension="csv",
        file_size_bytes=12048,
        content_type="text/csv",
        structure_status=StructureDetectionStatus.DETECTED,
        delimiter=DelimiterDetection(
            detected_delimiter=",",
            delimiter_label="comma",
            delimiter_confidence=DelimiterConfidence.HIGH,
            detection_reason="Comma produced the most consistent sampled row widths.",
        ),
        has_detected_header=True,
        header_row_index=0,
        column_names=["customer_name", "product", "amount"],
        detected_column_count=3,
        sampled_row_count=25,
        preview_row_count=2,
        warnings=[
            StructureWarning(
                code="leading_metadata_rows",
                message="Possible metadata rows were detected before the header.",
                severity=StructureWarningSeverity.WARNING,
            )
        ],
        preview=RawTablePreview(
            columns=["customer_name", "product", "amount"],
            rows=[["Ari", "Laptop", "12000000"], ["Justin", "Keyboard", "750000"]],
        ),
        next_step=StructureNextStep.QUALITY_ISSUE_DETECTION,
    )

    assert result.structure_status == StructureDetectionStatus.DETECTED
    assert result.delimiter is not None
    assert result.delimiter.delimiter_label == "comma"
    assert result.preview is not None
    assert result.preview.rows[0][0] == "Ari"


def test_raw_table_preview_requires_columns() -> None:
    with pytest.raises(ValidationError):
        RawTablePreview(columns=[], rows=[])
