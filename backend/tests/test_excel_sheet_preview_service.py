from io import BytesIO

from openpyxl import Workbook

from datapulse_api.models import StructureDetectionStatus
from datapulse_api.services.excel_structure_detection import detect_excel_sheet_preview


def workbook_bytes(rows: list[list[object]], sheet_name: str = "Sales") -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_name
    for row in rows:
        worksheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def detect(content: bytes, sheet_name: str = "Sales"):
    return detect_excel_sheet_preview(
        filename="workbook.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content=content,
        sheet_name=sheet_name,
    )


def warning_codes(result) -> set[str]:
    return {warning.code for warning in result.warnings}


def test_xlsx_selected_sheet_preview_detects_header_and_values() -> None:
    result = detect(workbook_bytes([["Customer", "Amount"], ["Ari", 1200], ["Justin", 750]]))

    assert result.structure_status == StructureDetectionStatus.DETECTED
    assert result.selected_sheet_name == "Sales"
    assert result.has_detected_header is True
    assert result.header_row_index == 0
    assert result.column_names == ["customer", "amount"]
    assert result.detected_column_count == 2
    assert result.preview is not None
    assert result.preview.rows == [["Ari", "1200"], ["Justin", "750"]]


def test_xlsx_no_header_generates_column_names() -> None:
    result = detect(workbook_bytes([["Ari", 1200], ["Justin", 750]]))

    assert result.has_detected_header is False
    assert result.generated_column_names is True
    assert result.column_names == ["column_1", "column_2"]
    assert result.preview is not None
    assert result.preview.rows[0] == ["Ari", "1200"]


def test_xlsx_empty_sheet_warning() -> None:
    result = detect(workbook_bytes([]))

    assert result.structure_status == StructureDetectionStatus.REJECTED
    assert "empty_sheet" in warning_codes(result)


def test_xlsx_duplicate_column_names_warning() -> None:
    result = detect(workbook_bytes([["Name", "Name", "Amount"], ["Ari", "Laptop", 1200]]))

    assert "duplicate_column_names" in warning_codes(result)


def test_xlsx_missing_column_names_warning() -> None:
    result = detect(workbook_bytes([["Name", None, "Amount"], ["Ari", "Laptop", 1200]]))

    assert "missing_column_names" in warning_codes(result)
    assert result.column_names == ["name", "column_2", "amount"]


def test_xlsx_empty_rows_and_columns_warning() -> None:
    result = detect(workbook_bytes([["Name", "Amount", None], [None, None, None], ["Ari", 1200, None]]))

    codes = warning_codes(result)
    assert "empty_rows_in_sample" in codes
    assert "empty_columns_in_sample" in codes


def test_selected_sheet_not_found_returns_warning() -> None:
    result = detect(workbook_bytes([["Customer", "Amount"], ["Ari", 1200]]), sheet_name="Missing")

    assert result.structure_status == StructureDetectionStatus.REJECTED
    assert result.warnings[0].code == "selected_sheet_not_found"


def test_xlsx_preview_is_bounded_to_twenty_rows() -> None:
    rows = [["Customer", "Amount"], *[[f"Person {index}", index] for index in range(25)]]
    result = detect(workbook_bytes(rows))

    assert result.preview_row_count == 20
    assert result.preview is not None
    assert len(result.preview.rows) == 20


def test_xlsx_sample_limit_warning() -> None:
    rows = [["Customer", "Amount"], *[[f"Person {index}", index] for index in range(60)]]
    result = detect(workbook_bytes(rows))

    assert "sample_row_limit_reached" in warning_codes(result)
