from fastapi.testclient import TestClient
from io import BytesIO
from openpyxl import Workbook

from datapulse_api.main import app


def post_detect(
    filename: str,
    content: bytes,
    content_type: str,
    sheet_name: str | None = None,
) -> dict[str, object]:
    client = TestClient(app)
    data = {"sheet_name": sheet_name} if sheet_name is not None else None
    response = client.post(
        "/files/detect-structure",
        files={"file": (filename, content, content_type)},
        data=data,
    )

    assert response.status_code == 200
    return response.json()


def make_xlsx() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sales"
    worksheet.append(["Customer", "Amount"])
    worksheet.append(["Ari", 1200])
    workbook.create_sheet("Customers")
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def warning_codes(payload: dict[str, object]) -> set[str]:
    return {warning["code"] for warning in payload["warnings"]}


def test_detect_structure_accepts_comma_csv() -> None:
    payload = post_detect("sales.csv", b"name,amount\nAri,1200\n", "text/csv")

    assert payload["structure_status"] == "detected"
    assert payload["detected_extension"] == "csv"
    assert payload["delimiter"]["detected_delimiter"] == ","
    assert payload["delimiter"]["delimiter_label"] == "comma"
    assert payload["has_detected_header"] is True
    assert payload["column_names"] == ["name", "amount"]
    assert payload["preview"]["rows"] == [["Ari", "1200"]]


def test_detect_structure_accepts_tsv() -> None:
    payload = post_detect("sales.tsv", b"name\tamount\nAri\t1200\n", "text/tab-separated-values")

    assert payload["structure_status"] == "detected"
    assert payload["delimiter"]["delimiter_label"] == "tab"


def test_detect_structure_accepts_pipe_txt() -> None:
    payload = post_detect("sales.txt", b"name|amount\nAri|1200\n", "text/plain")

    assert payload["structure_status"] == "detected"
    assert payload["delimiter"]["delimiter_label"] == "pipe"


def test_detect_structure_discovers_excel_sheets() -> None:
    payload = post_detect(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    assert payload["structure_status"] == "sheet_selection_required"
    assert payload["next_step"] == "select_excel_sheet"
    assert payload["workbook"]["sheet_names"] == ["Sales", "Customers"]
    assert payload["workbook"]["default_sheet_name"] == "Sales"
    assert payload["warnings"][0]["code"] == "excel_formatting_not_preserved"


def test_detect_structure_previews_selected_excel_sheet() -> None:
    payload = post_detect(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        sheet_name="Sales",
    )

    assert payload["structure_status"] == "detected"
    assert payload["selected_sheet_name"] == "Sales"
    assert payload["has_detected_header"] is True
    assert payload["column_names"] == ["customer", "amount"]
    assert payload["preview"]["rows"] == [["Ari", "1200"]]


def test_detect_structure_rejects_missing_excel_sheet() -> None:
    payload = post_detect(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        sheet_name="Missing",
    )

    assert payload["structure_status"] == "rejected"
    assert payload["warnings"][0]["code"] == "selected_sheet_not_found"


def test_detect_structure_rejects_unsupported_pdf() -> None:
    payload = post_detect("document.pdf", b"%PDF", "application/pdf")

    assert payload["structure_status"] == "rejected"
    assert payload["next_step"] == "upload_supported_file"


def test_detect_structure_rejects_empty_file() -> None:
    payload = post_detect("empty.csv", b"", "text/csv")

    assert payload["structure_status"] == "rejected"
    assert payload["next_step"] == "upload_supported_file"


def test_detect_structure_sanitizes_unsafe_filename() -> None:
    payload = post_detect("../../private/sales.csv", b"name,amount\nAri,1200\n", "text/csv")

    assert payload["original_filename"] == "../../private/sales.csv"
    assert payload["safe_filename"] == "sales.csv"


def test_detect_structure_preview_is_bounded() -> None:
    rows = "\n".join(f"Person {index},{index}" for index in range(25))
    payload = post_detect("many.csv", f"name,amount\n{rows}\n".encode("utf-8"), "text/csv")

    assert payload["preview_row_count"] == 20
    assert len(payload["preview"]["rows"]) == 20


def test_detect_structure_reports_warnings() -> None:
    payload = post_detect(
        "messy.csv",
        b"Report\nGenerated\nname,name,amount\nAri,Laptop\n\nJustin,Keyboard,75,extra\n",
        "text/csv",
    )

    codes = warning_codes(payload)
    assert "leading_metadata_rows" in codes
    assert "duplicate_column_names" in codes
    assert "empty_rows_in_sample" in codes
