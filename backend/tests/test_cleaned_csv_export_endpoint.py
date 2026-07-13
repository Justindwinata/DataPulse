from io import BytesIO
import json

from fastapi.testclient import TestClient
from openpyxl import Workbook

from datapulse_api.main import app


def post_export(
    filename: str,
    content: bytes,
    content_type: str,
    rules: list[str] | None = None,
    sheet_name: str | None = None,
):
    client = TestClient(app)
    data: dict[str, object] = {}
    if rules is not None:
        data["rules"] = json.dumps(rules)
    if sheet_name is not None:
        data["sheet_name"] = sheet_name
    return client.post(
        "/files/export-cleaned-csv",
        files={"file": (filename, content, content_type)},
        data=data,
    )


def make_xlsx() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sales"
    worksheet.append(["Customer Name", "Amount", "Empty"])
    worksheet.append([" Ari ", 1200, None])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_export_cleaned_csv_download_response() -> None:
    response = post_export(
        "messy.csv",
        b"Customer Name,Empty\n Ari ,\n",
        "text/csv",
        ["trim_whitespace", "drop_empty_columns", "standardize_column_names"],
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == 'attachment; filename="messy_cleaned.csv"'
    assert response.text == "customer_name\nAri\n"


def test_export_cleaned_csv_escapes_values() -> None:
    response = post_export("escaping.csv", b'name,note\n"Ari, D","Line ""one""\nLine two"\n', "text/csv", [])

    assert response.status_code == 200
    assert response.text == 'name,note\n"Ari, D","Line ""one""\nLine two"\n'


def test_export_selected_excel_sheet_as_csv() -> None:
    response = post_export(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ["trim_whitespace", "drop_empty_columns", "standardize_column_names"],
        sheet_name="Sales",
    )

    assert response.status_code == 200
    assert response.text == "customer_name,amount\nAri,1200\n"


def test_export_excel_without_sheet_name_returns_error() -> None:
    response = post_export(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ["trim_whitespace"],
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "sheet_selection_required"


def test_export_rejects_unsupported_pdf() -> None:
    response = post_export("document.pdf", b"%PDF", "application/pdf", ["trim_whitespace"])

    assert response.status_code == 400


def test_export_rejects_empty_file() -> None:
    response = post_export("empty.csv", b"", "text/csv", [])

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "empty_file"


def test_existing_cleaning_preview_endpoint_still_works() -> None:
    client = TestClient(app)
    response = client.post(
        "/files/apply-cleaning-preview",
        files={"file": ("messy.csv", b"name\n Ari \n", "text/csv")},
        data={"rules": json.dumps(["trim_whitespace"])},
    )

    assert response.status_code == 200
