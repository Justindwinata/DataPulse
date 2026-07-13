from io import BytesIO
import json

from fastapi.testclient import TestClient
from openpyxl import Workbook

from datapulse_api.main import app


def post_report(
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
        "/files/cleaning-report.html",
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


def test_html_report_for_csv_returns_standalone_html() -> None:
    response = post_report(
        "messy.csv",
        b"Customer Name,Amount\n Ari ,1200\n Ari ,1200\n",
        "text/csv",
        ["trim_whitespace", "remove_duplicate_rows", "standardize_column_names"],
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "DataPulse Cleaning Report" in response.text
    assert "Data Quality Summary" in response.text
    assert "Rule Effects" in response.text
    assert "Export Summary" in response.text
    assert "remove_duplicate_rows" in response.text


def test_html_report_for_tsv() -> None:
    response = post_report(
        "sales.tsv",
        b"Customer Name\tAmount\n Ari \t1200\n",
        "text/tab-separated-values",
        ["trim_whitespace", "standardize_column_names"],
    )

    assert response.status_code == 200
    assert "tab" in response.text
    assert "customer_name" in response.text


def test_html_report_for_xlsx_selected_sheet() -> None:
    response = post_report(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ["trim_whitespace", "drop_empty_columns", "standardize_column_names"],
        sheet_name="Sales",
    )

    assert response.status_code == 200
    assert "Selected sheet:" in response.text
    assert "Sales" in response.text
    assert "Excel values are exported only as CSV" in response.text


def test_html_report_for_excel_without_sheet_name_requires_selection() -> None:
    response = post_report(
        "workbook.xlsx",
        make_xlsx(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ["trim_whitespace"],
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "sheet_selection_required"


def test_html_report_rejects_unsupported_pdf() -> None:
    response = post_report("document.pdf", b"%PDF", "application/pdf", ["trim_whitespace"])

    assert response.status_code == 400


def test_html_report_rejects_empty_file() -> None:
    response = post_report("empty.csv", b"", "text/csv", [])

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "empty_file"


def test_html_report_escapes_filename_and_cell_values() -> None:
    response = post_report(
        '"><script>alert(1)</script>.csv',
        b'name,note\n"<b>Ari</b>","<script>bad()</script>"\n',
        "text/csv",
        ["trim_whitespace"],
    )

    assert response.status_code == 200
    assert "<script" not in response.text.lower()
    assert "&lt;b&gt;Ari&lt;/b&gt;" in response.text
    assert "&lt;script&gt;bad()&lt;/script&gt;" in response.text


def test_existing_export_endpoint_still_works_after_report_route_added() -> None:
    client = TestClient(app)
    response = client.post(
        "/files/export-cleaned-csv",
        files={"file": ("messy.csv", b"name,amount\n Ari ,10\n", "text/csv")},
        data={"rules": json.dumps(["trim_whitespace"])},
    )

    assert response.status_code == 200
    assert response.text == "name,amount\nAri,10\n"
