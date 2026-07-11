from datapulse_api.models import StructureDetectionStatus
from datapulse_api.services.csv_structure_detection import detect_csv_like_structure


def detect(filename: str, content: str, content_type: str = "text/csv"):
    return detect_csv_like_structure(
        filename=filename,
        content_type=content_type,
        content=content.encode("utf-8"),
    )


def warning_codes(result) -> set[str]:
    return {warning.code for warning in result.warnings}


def test_detects_comma_csv_with_header_and_preview() -> None:
    result = detect("sales.csv", "name,product,amount\nAri,Laptop,1200\nJustin,Keyboard,75\n")

    assert result.structure_status == StructureDetectionStatus.DETECTED
    assert result.delimiter is not None
    assert result.delimiter.detected_delimiter == ","
    assert result.delimiter.delimiter_label == "comma"
    assert result.has_detected_header is True
    assert result.header_row_index == 0
    assert result.column_names == ["name", "product", "amount"]
    assert result.detected_column_count == 3
    assert result.preview is not None
    assert result.preview.rows == [["Ari", "Laptop", "1200"], ["Justin", "Keyboard", "75"]]


def test_detects_semicolon_csv() -> None:
    result = detect("sales.csv", "name;product;amount\nAri;Laptop;1200\n")

    assert result.delimiter is not None
    assert result.delimiter.detected_delimiter == ";"
    assert result.delimiter.delimiter_label == "semicolon"


def test_detects_tab_tsv() -> None:
    result = detect("sales.tsv", "name\tproduct\tamount\nAri\tLaptop\t1200\n", "text/tab-separated-values")

    assert result.delimiter is not None
    assert result.delimiter.detected_delimiter == "\t"
    assert result.delimiter.delimiter_label == "tab"


def test_detects_pipe_delimited_txt() -> None:
    result = detect("sales.txt", "name|product|amount\nAri|Laptop|1200\n", "text/plain")

    assert result.delimiter is not None
    assert result.delimiter.detected_delimiter == "|"
    assert result.delimiter.delimiter_label == "pipe"


def test_no_header_file_generates_column_names() -> None:
    result = detect("no_header.csv", "Ari,Laptop,1200\nJustin,Keyboard,75\n")

    assert result.has_detected_header is False
    assert result.generated_column_names is True
    assert result.column_names == ["column_1", "column_2", "column_3"]
    assert result.preview is not None
    assert result.preview.rows[0] == ["Ari", "Laptop", "1200"]


def test_leading_metadata_rows_before_header_add_warning() -> None:
    result = detect("metadata.csv", "Sales export\nGenerated 2026\nname,amount\nAri,1200\n")

    assert result.has_detected_header is True
    assert result.header_row_index == 2
    assert "leading_metadata_rows" in warning_codes(result)


def test_inconsistent_row_widths_add_warning_and_preview_is_normalized() -> None:
    result = detect("messy.csv", "name,product,amount\nAri,Laptop\nJustin,Keyboard,75,extra\n")

    assert "inconsistent_row_widths" in warning_codes(result)
    assert result.preview is not None
    assert result.preview.rows[0] == ["Ari", "Laptop", ""]
    assert result.preview.rows[1] == ["Justin", "Keyboard", "75"]


def test_duplicate_column_names_add_warning() -> None:
    result = detect("duplicates.csv", "name,name,amount\nAri,Laptop,1200\n")

    assert "duplicate_column_names" in warning_codes(result)


def test_missing_column_names_add_warning() -> None:
    result = detect("missing_headers.csv", "name,,amount\nAri,Laptop,1200\n")

    assert "missing_column_names" in warning_codes(result)
    assert result.column_names == ["name", "column_2", "amount"]


def test_empty_rows_add_warning() -> None:
    result = detect("empty_rows.csv", "name,amount\n\nAri,1200\n")

    assert "empty_rows_in_sample" in warning_codes(result)


def test_excel_returns_honest_limitation() -> None:
    result = detect_csv_like_structure(
        filename="workbook.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content=b"placeholder workbook bytes",
    )

    assert result.structure_status == StructureDetectionStatus.NOT_IMPLEMENTED
    assert result.warnings[0].code == "excel_structure_detection_not_implemented"
    assert "later milestone" in result.warnings[0].message


def test_unsupported_pdf_is_rejected() -> None:
    result = detect_csv_like_structure(
        filename="document.pdf",
        content_type="application/pdf",
        content=b"%PDF",
    )

    assert result.structure_status == StructureDetectionStatus.REJECTED
    assert result.next_step.value == "upload_supported_file"


def test_empty_file_is_rejected() -> None:
    result = detect_csv_like_structure(filename="empty.csv", content_type="text/csv", content=b"")

    assert result.structure_status == StructureDetectionStatus.REJECTED
    assert result.warnings[0].code == "file_not_supported_for_structure_detection"


def test_unsafe_filename_is_sanitized() -> None:
    result = detect("../../private/sales.csv", "name,amount\nAri,1200\n")

    assert result.original_filename == "../../private/sales.csv"
    assert result.safe_filename == "sales.csv"


def test_preview_is_bounded_to_twenty_rows() -> None:
    rows = "\n".join(f"Person {index},{index}" for index in range(25))
    result = detect("many.csv", f"name,amount\n{rows}\n")

    assert result.preview_row_count == 20
    assert result.preview is not None
    assert len(result.preview.rows) == 20
