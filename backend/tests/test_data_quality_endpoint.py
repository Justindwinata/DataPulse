from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook

from datapulse_api.main import app


def post_quality(
    filename: str,
    content: bytes,
    content_type: str,
    sheet_name: str | None = None,
) -> dict[str, object]:
    client = TestClient(app)
    data = {"sheet_name": sheet_name} if sheet_name is not None else None
    response = client.post(
        "/files/detect-quality",
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
    worksheet.append(["Justin", None])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def issue_codes(payload: dict[str, object]) -> set[str]:
    return {issue["code"] for issue in payload["issues"]}


def test_detect_quality_profiles_csv_file() -> None:
    payload = post_quality(
        "sales.csv",
        b"name,amount\nAri,1200\nJustin,\n",
        "text/csv",
    )

    assert payload["quality_status"] == "profiled"
    assert payload["detected_extension"] == "csv"
    assert payload["detected_column_count"] == 2
    assert "missing_values" in issue_codes(payload)
    assert payload["next_step"] == "cleaning_rules"


def test_detect_quality_profiles_selected_excel_sheet() -> None:
    payload = post_quality(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        sheet_name="Sales",
    )

    assert payload["quality_status"] == "profiled"
    assert payload["selected_sheet_name"] == "Sales"
    assert "missing_values" in issue_codes(payload)


def test_detect_quality_requires_excel_sheet_selection() -> None:
    payload = post_quality(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    assert payload["quality_status"] == "sheet_selection_required"
    assert payload["next_step"] == "select_excel_sheet"
    assert payload["messages"] == ["Select an Excel sheet before running data quality profiling."]


def test_detect_quality_rejects_unsupported_pdf() -> None:
    payload = post_quality("document.pdf", b"%PDF", "application/pdf")

    assert payload["quality_status"] == "rejected"
    assert payload["next_step"] == "upload_supported_file"


def test_detect_quality_rejects_empty_file() -> None:
    payload = post_quality("empty.csv", b"", "text/csv")

    assert payload["quality_status"] == "rejected"
    assert payload["messages"] == ["File is empty. Upload a non-empty tabular file."]


def test_existing_structure_endpoint_still_profiles_csv_structure() -> None:
    client = TestClient(app)
    response = client.post(
        "/files/detect-structure",
        files={"file": ("sales.csv", b"name,amount\nAri,1200\n", "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["structure_status"] == "detected"
    assert payload["next_step"] == "quality_issue_detection"
