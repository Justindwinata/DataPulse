from fastapi.testclient import TestClient

from datapulse_api.main import app
from datapulse_api.services.file_validation import MAX_UPLOAD_SIZE_BYTES


def post_upload(filename: str, content: bytes, content_type: str) -> dict[str, object]:
    client = TestClient(app)
    response = client.post(
        "/files/validate-upload",
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 200
    return response.json()


def test_validate_upload_accepts_valid_csv() -> None:
    payload = post_upload("messy_sales.csv", b"name,total\nAda,10\n", "text/csv")

    assert payload["original_filename"] == "messy_sales.csv"
    assert payload["detected_extension"] == "csv"
    assert payload["content_type"] == "text/csv"
    assert payload["file_size_bytes"] == 18
    assert payload["is_supported"] is True
    assert payload["validation_status"] == "accepted"
    assert payload["next_step"] == "structure_detection"
    assert payload["structure_detection_available"] is False


def test_validate_upload_accepts_valid_tsv() -> None:
    payload = post_upload("rows.tsv", b"name\ttotal\nAda\t10\n", "text/tab-separated-values")

    assert payload["detected_extension"] == "tsv"
    assert payload["is_supported"] is True


def test_validate_upload_accepts_valid_txt() -> None:
    payload = post_upload("table.txt", b"name | total\nAda | 10\n", "text/plain")

    assert payload["detected_extension"] == "txt"
    assert payload["is_supported"] is True


def test_validate_upload_accepts_valid_xlsx_extension_without_parsing() -> None:
    payload = post_upload(
        "workbook.xlsx",
        b"placeholder workbook bytes",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    assert payload["detected_extension"] == "xlsx"
    assert payload["is_supported"] is True


def test_validate_upload_accepts_valid_xls_extension_without_parsing() -> None:
    payload = post_upload("legacy.xls", b"legacy workbook bytes", "application/vnd.ms-excel")

    assert payload["detected_extension"] == "xls"
    assert payload["is_supported"] is True


def test_validate_upload_rejects_unsupported_pdf() -> None:
    payload = post_upload("document.pdf", b"%PDF-1.4", "application/pdf")

    assert payload["detected_extension"] == "pdf"
    assert payload["is_supported"] is False
    assert payload["validation_status"] == "rejected"
    assert payload["next_step"] == "upload_supported_file"


def test_validate_upload_rejects_empty_file() -> None:
    payload = post_upload("empty.csv", b"", "text/csv")

    assert payload["is_supported"] is False
    assert payload["validation_status"] == "rejected"
    assert any("File is empty" in message for message in payload["validation_messages"])


def test_validate_upload_rejects_oversized_file() -> None:
    payload = post_upload("large.csv", b"x" * (MAX_UPLOAD_SIZE_BYTES + 1), "text/csv")

    assert payload["is_supported"] is False
    assert payload["validation_status"] == "rejected"
    assert "File size exceeds the 10 MB limit." in payload["validation_messages"]


def test_validate_upload_sanitizes_unsafe_filename() -> None:
    payload = post_upload("../../private/messy.csv", b"name,total\nAda,10\n", "text/csv")

    assert payload["original_filename"] == "../../private/messy.csv"
    assert payload["safe_filename"] == "messy.csv"
    assert payload["is_supported"] is True


def test_validate_upload_response_shape() -> None:
    payload = post_upload("messy_sales.csv", b"name,total\nAda,10\n", "text/csv")

    assert set(payload) == {
        "original_filename",
        "safe_filename",
        "detected_extension",
        "content_type",
        "file_size_bytes",
        "max_size_bytes",
        "is_supported",
        "validation_status",
        "validation_messages",
        "next_step",
        "structure_detection_available",
    }
