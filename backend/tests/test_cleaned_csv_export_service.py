from io import BytesIO

import pytest
from openpyxl import Workbook

from datapulse_api.models import CleaningRuleCode
from datapulse_api.services.cleaned_csv_export import (
    CleanedCsvExportError,
    export_cleaned_csv,
)


def export_text(filename: str, content: bytes, rules: list[CleaningRuleCode], content_type: str = "text/csv") -> str:
    result = export_cleaned_csv(
        filename=filename,
        content_type=content_type,
        content=content,
        rules=rules,
    )
    return result.content.decode("utf-8")


def make_xlsx() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sales"
    worksheet.append(["Customer Name", "Amount", "Empty"])
    worksheet.append([" Ari ", 1200, None])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_csv_export_with_trim_whitespace() -> None:
    text = export_text("messy.csv", b"name,amount\n Ari ,1200\n", [CleaningRuleCode.TRIM_WHITESPACE])

    assert text == "name,amount\nAri,1200\n"


def test_csv_export_with_remove_empty_rows() -> None:
    text = export_text("rows.csv", b"name,amount\nAri,10\n,\n", [CleaningRuleCode.REMOVE_EMPTY_ROWS])

    assert text == "name,amount\nAri,10\n"


def test_csv_export_with_remove_duplicate_rows() -> None:
    text = export_text("dupes.csv", b"name,amount\nAri,10\nAri,10\n", [CleaningRuleCode.REMOVE_DUPLICATE_ROWS])

    assert text == "name,amount\nAri,10\n"


def test_csv_export_with_drop_empty_columns() -> None:
    text = export_text("empty-col.csv", b"name,empty\nAri,\n", [CleaningRuleCode.DROP_EMPTY_COLUMNS])

    assert text == "name\nAri\n"


def test_csv_export_with_standardize_column_names() -> None:
    text = export_text("headers.csv", b"Customer Name,Amount!\nAri,10\n", [CleaningRuleCode.STANDARDIZE_COLUMN_NAMES])

    assert text == "customer_name,amount\nAri,10\n"


def test_csv_export_with_generate_missing_column_names() -> None:
    text = export_text("headers.csv", b"name,email,\nAri,a@example.com,10\n", [CleaningRuleCode.GENERATE_MISSING_COLUMN_NAMES])

    assert text == "name,email,column_3\nAri,a@example.com,10\n"


def test_multiple_rules_applied_together() -> None:
    text = export_text(
        "combo.csv",
        b"Customer Name,Empty\n Ari ,\n Ari ,\n,\n",
        [
            CleaningRuleCode.TRIM_WHITESPACE,
            CleaningRuleCode.REMOVE_EMPTY_ROWS,
            CleaningRuleCode.REMOVE_DUPLICATE_ROWS,
            CleaningRuleCode.DROP_EMPTY_COLUMNS,
            CleaningRuleCode.STANDARDIZE_COLUMN_NAMES,
        ],
    )

    assert text == "customer_name\nAri\n"


def test_tsv_input_exports_as_csv() -> None:
    text = export_text("sales.tsv", b"name\tamount\n Ari \t10\n", [CleaningRuleCode.TRIM_WHITESPACE], "text/tab-separated-values")

    assert text == "name,amount\nAri,10\n"


def test_excel_selected_sheet_exports_as_csv() -> None:
    result = export_cleaned_csv(
        filename="workbook.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content=make_xlsx(),
        sheet_name="Sales",
        rules=[
            CleaningRuleCode.TRIM_WHITESPACE,
            CleaningRuleCode.DROP_EMPTY_COLUMNS,
            CleaningRuleCode.STANDARDIZE_COLUMN_NAMES,
        ],
    )

    assert result.filename == "workbook_cleaned.csv"
    assert result.content.decode("utf-8") == "customer_name,amount\nAri,1200\n"


def test_excel_without_sheet_name_requires_selection() -> None:
    with pytest.raises(CleanedCsvExportError) as error:
        export_cleaned_csv(
            filename="workbook.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            content=make_xlsx(),
            rules=[CleaningRuleCode.TRIM_WHITESPACE],
        )

    assert error.value.code == "sheet_selection_required"


def test_unsupported_pdf_rejected() -> None:
    with pytest.raises(CleanedCsvExportError):
        export_cleaned_csv(
            filename="document.pdf",
            content_type="application/pdf",
            content=b"%PDF",
            rules=[CleaningRuleCode.TRIM_WHITESPACE],
        )


def test_empty_file_rejected() -> None:
    with pytest.raises(CleanedCsvExportError) as error:
        export_cleaned_csv(filename="empty.csv", content_type="text/csv", content=b"", rules=[])

    assert error.value.code == "empty_file"


def test_csv_escaping_for_commas_quotes_and_newlines() -> None:
    text = export_text(
        "escaping.csv",
        b'name,note\n"Ari, D","Line ""one""\nLine two"\n',
        [],
    )

    assert text == 'name,note\n"Ari, D","Line ""one""\nLine two"\n'


def test_no_rules_selected_exports_detected_table_deterministically() -> None:
    text = export_text("no-rules.csv", b"name,amount\n Ari ,10\n", [])

    assert text == "name,amount\n Ari ,10\n"


def test_safe_export_filename_from_unsafe_source_name() -> None:
    result = export_cleaned_csv(
        filename="../../Messy Sales!.csv",
        content_type="text/csv",
        content=b"name\nAri\n",
        rules=[],
    )

    assert result.filename == "Messy_Sales_cleaned.csv"


def test_export_handles_all_columns_dropped() -> None:
    text = export_text("empty-columns.csv", b"left,right\n,\n", [CleaningRuleCode.DROP_EMPTY_COLUMNS])

    assert text == "\n\n"
