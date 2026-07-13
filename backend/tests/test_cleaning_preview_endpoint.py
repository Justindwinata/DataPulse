from io import BytesIO
import json

from fastapi.testclient import TestClient
from openpyxl import Workbook

from datapulse_api.main import app


def post_cleaning(
    filename: str,
    content: bytes,
    content_type: str,
    rules: list[str] | None = None,
    sheet_name: str | None = None,
) -> dict[str, object]:
    client = TestClient(app)
    data: dict[str, object] = {}
    if rules is not None:
        data["rules"] = json.dumps(rules)
    if sheet_name is not None:
        data["sheet_name"] = sheet_name
    response = client.post(
        "/files/apply-cleaning-preview",
        files={"file": (filename, content, content_type)},
        data=data,
    )
    assert response.status_code == 200
    return response.json()


def make_xlsx() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sales"
    worksheet.append(["Customer Name", "Amount", "Empty"])
    worksheet.append([" Ari ", 1200, None])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_apply_cleaning_preview_profiles_csv_rules() -> None:
    payload = post_cleaning(
        "messy.csv",
        b"Customer Name,Empty\n Ari ,\n,\n",
        "text/csv",
        ["trim_whitespace", "remove_empty_rows", "drop_empty_columns", "standardize_column_names"],
    )

    assert payload["cleaning_status"] == "preview_generated"
    assert payload["cleaned_preview"]["columns"] == ["customer_name"]
    assert payload["cleaned_preview"]["rows"] == [["Ari"]]
    assert payload["after_summary"]["removed_empty_rows_count"] == 1
    assert payload["after_summary"]["dropped_empty_columns_count"] == 1


def test_apply_cleaning_preview_accepts_tsv() -> None:
    payload = post_cleaning(
        "messy.tsv",
        b"name\tamount\n Ari \t10\n",
        "text/tab-separated-values",
        ["trim_whitespace"],
    )

    assert payload["cleaning_status"] == "preview_generated"
    assert payload["cleaned_preview"]["rows"] == [["Ari", "10"]]


def test_apply_cleaning_preview_profiles_xlsx_selected_sheet() -> None:
    payload = post_cleaning(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ["trim_whitespace", "drop_empty_columns", "standardize_column_names"],
        sheet_name="Sales",
    )

    assert payload["cleaning_status"] == "preview_generated"
    assert payload["selected_sheet_name"] == "Sales"
    assert payload["cleaned_preview"]["columns"] == ["customer_name", "amount"]


def test_apply_cleaning_preview_requires_excel_sheet_name() -> None:
    payload = post_cleaning(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ["trim_whitespace"],
    )

    assert payload["cleaning_status"] == "sheet_selection_required"
    assert payload["next_step"] == "select_excel_sheet"


def test_apply_cleaning_preview_rejects_pdf() -> None:
    payload = post_cleaning("document.pdf", b"%PDF", "application/pdf", ["trim_whitespace"])

    assert payload["cleaning_status"] == "rejected"


def test_apply_cleaning_preview_rejects_empty_file() -> None:
    payload = post_cleaning("empty.csv", b"", "text/csv", ["trim_whitespace"])

    assert payload["cleaning_status"] == "rejected"
    assert payload["warnings"][0]["message"] == "File is empty. Upload a non-empty tabular file."


def test_existing_quality_endpoint_still_works() -> None:
    client = TestClient(app)
    response = client.post(
        "/files/detect-quality",
        files={"file": ("sales.csv", b"name,amount\nAri,\n", "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["quality_status"] == "profiled"
