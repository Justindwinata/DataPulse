from datapulse_api.models import UploadNextStep, UploadValidationStatus
from datapulse_api.services.file_validation import (
    MAX_UPLOAD_SIZE_BYTES,
    detect_extension,
    sanitize_filename,
    validate_uploaded_file_metadata,
)


def test_validate_uploaded_file_metadata_accepts_valid_csv() -> None:
    result = validate_uploaded_file_metadata(
        filename="messy_sales.csv",
        content_type="text/csv",
        file_size_bytes=128,
    )

    assert result.original_filename == "messy_sales.csv"
    assert result.safe_filename == "messy_sales.csv"
    assert result.detected_extension == "csv"
    assert result.is_supported is True
    assert result.validation_status == UploadValidationStatus.ACCEPTED
    assert result.next_step == UploadNextStep.STRUCTURE_DETECTION
    assert result.structure_detection_available is False


def test_validate_uploaded_file_metadata_accepts_supported_extensions() -> None:
    for filename, content_type in [
        ("rows.tsv", "text/tab-separated-values"),
        ("notes.txt", "text/plain"),
        ("workbook.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("legacy.xls", "application/vnd.ms-excel"),
    ]:
        result = validate_uploaded_file_metadata(
            filename=filename,
            content_type=content_type,
            file_size_bytes=128,
        )

        assert result.is_supported is True
        assert result.validation_status == UploadValidationStatus.ACCEPTED


def test_validate_uploaded_file_metadata_rejects_pdf() -> None:
    result = validate_uploaded_file_metadata(
        filename="document.pdf",
        content_type="application/pdf",
        file_size_bytes=1024,
    )

    assert result.detected_extension == "pdf"
    assert result.is_supported is False
    assert result.validation_status == UploadValidationStatus.REJECTED
    assert result.next_step == UploadNextStep.UPLOAD_SUPPORTED_FILE
    assert "Unsupported file extension" in result.validation_messages[0]


def test_validate_uploaded_file_metadata_rejects_empty_file() -> None:
    result = validate_uploaded_file_metadata(
        filename="empty.csv",
        content_type="text/csv",
        file_size_bytes=0,
    )

    assert result.is_supported is False
    assert result.validation_status == UploadValidationStatus.REJECTED
    assert any("File is empty" in message for message in result.validation_messages)


def test_validate_uploaded_file_metadata_rejects_oversized_file() -> None:
    result = validate_uploaded_file_metadata(
        filename="large.csv",
        content_type="text/csv",
        file_size_bytes=MAX_UPLOAD_SIZE_BYTES + 1,
    )

    assert result.is_supported is False
    assert result.validation_status == UploadValidationStatus.REJECTED
    assert "File size exceeds the 10 MB limit." in result.validation_messages


def test_sanitize_filename_strips_path_traversal_segments() -> None:
    assert sanitize_filename("../../private/messy.csv") == "messy.csv"
    assert sanitize_filename("..\\private\\messy.csv") == "messy.csv"


def test_detect_extension_is_lowercase_and_safe() -> None:
    assert detect_extension("../../MESSY.CSV") == "csv"
    assert detect_extension("no_extension") == ""
