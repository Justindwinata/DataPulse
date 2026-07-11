import pytest
from pydantic import ValidationError

from datapulse_api.models import (
    SUPPORTED_UPLOAD_EXTENSIONS,
    FileUploadValidationResponse,
    UploadNextStep,
    UploadValidationStatus,
)


def test_upload_validation_status_values_are_stable_api_contracts() -> None:
    assert UploadValidationStatus.ACCEPTED.value == "accepted"
    assert UploadValidationStatus.REJECTED.value == "rejected"


def test_upload_next_step_values_are_stable_api_contracts() -> None:
    assert UploadNextStep.STRUCTURE_DETECTION.value == "structure_detection"
    assert UploadNextStep.UPLOAD_SUPPORTED_FILE.value == "upload_supported_file"


def test_supported_upload_extensions_match_dp_0002_scope() -> None:
    assert SUPPORTED_UPLOAD_EXTENSIONS == frozenset({"csv", "tsv", "txt", "xlsx", "xls"})


def test_file_upload_validation_response_accepts_expected_shape() -> None:
    response = FileUploadValidationResponse(
        original_filename="messy_sales.csv",
        safe_filename="messy_sales.csv",
        detected_extension="csv",
        content_type="text/csv",
        file_size_bytes=24512,
        max_size_bytes=10 * 1024 * 1024,
        is_supported=True,
        validation_status=UploadValidationStatus.ACCEPTED,
        validation_messages=[
            "File extension is supported.",
            "File size is within the 10 MB limit.",
        ],
        next_step=UploadNextStep.STRUCTURE_DETECTION,
    )

    assert response.structure_detection_available is False
    assert response.model_dump()["validation_status"] == UploadValidationStatus.ACCEPTED


def test_file_upload_validation_response_requires_messages() -> None:
    with pytest.raises(ValidationError):
        FileUploadValidationResponse(
            original_filename="empty.csv",
            safe_filename="empty.csv",
            detected_extension="csv",
            content_type="text/csv",
            file_size_bytes=0,
            max_size_bytes=10 * 1024 * 1024,
            is_supported=False,
            validation_status=UploadValidationStatus.REJECTED,
            validation_messages=[],
            next_step=UploadNextStep.UPLOAD_SUPPORTED_FILE,
        )
