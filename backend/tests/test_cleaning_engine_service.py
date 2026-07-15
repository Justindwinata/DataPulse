from io import BytesIO

from openpyxl import Workbook

from datapulse_api.models import CleaningRuleCode
from datapulse_api.services.cleaning_engine import generate_cleaning_preview


def make_xlsx() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sales"
    worksheet.append(["Customer Name", "Amount", "Empty"])
    worksheet.append([" Ari ", 1200, None])
    worksheet.append(["Ari", 1200, None])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_no_rules_selected_returns_warning_and_original_preview() -> None:
    result = generate_cleaning_preview(
        filename="messy.csv",
        content_type="text/csv",
        content=b"name,amount\n Ari ,1200\n",
        rules=[],
    )

    assert result.cleaning_status == "preview_generated"
    assert result.applied_rules == []
    assert result.cleaned_preview.rows == [[" Ari ", "1200"]]
    assert {warning.code for warning in result.warnings} >= {"no_rules_selected", "sample_based_preview"}


def test_trim_whitespace() -> None:
    result = generate_cleaning_preview(
        filename="messy.csv",
        content_type="text/csv",
        content=b"name,amount\n Ari ,10\n",
        rules=[CleaningRuleCode.TRIM_WHITESPACE],
    )

    assert result.cleaned_preview.rows == [["Ari", "10"]]
    assert result.rule_effects[0].affected_rows == 1


def test_remove_empty_rows() -> None:
    result = generate_cleaning_preview(
        filename="rows.csv",
        content_type="text/csv",
        content=b"name,amount\nAri,10\n,\nJustin,20\n",
        rules=[CleaningRuleCode.REMOVE_EMPTY_ROWS],
    )

    assert result.after_summary.removed_empty_rows_count == 1
    assert result.after_summary.row_count == 2


def test_remove_duplicate_rows() -> None:
    result = generate_cleaning_preview(
        filename="dupes.csv",
        content_type="text/csv",
        content=b"name,amount\nAri,10\nAri,10\n",
        rules=[CleaningRuleCode.REMOVE_DUPLICATE_ROWS],
    )

    assert result.after_summary.removed_duplicate_rows_count == 1
    assert result.cleaned_preview.rows == [["Ari", "10"]]


def test_drop_empty_columns() -> None:
    result = generate_cleaning_preview(
        filename="columns.csv",
        content_type="text/csv",
        content=b"name,empty\nAri,\nJustin,\n",
        rules=[CleaningRuleCode.DROP_EMPTY_COLUMNS],
    )

    assert result.after_summary.dropped_empty_columns_count == 1
    assert result.cleaned_preview.columns == ["name"]


def test_standardize_column_names() -> None:
    result = generate_cleaning_preview(
        filename="headers.csv",
        content_type="text/csv",
        content=b"Customer Name,Order Amount!\nAri,10\n",
        rules=[CleaningRuleCode.STANDARDIZE_COLUMN_NAMES],
    )

    assert result.cleaned_preview.columns == ["customer_name", "order_amount"]
    assert result.after_summary.renamed_columns_count == 1


def test_generate_missing_column_names() -> None:
    result = generate_cleaning_preview(
        filename="missing.csv",
        content_type="text/csv",
        content=b"name,email,\nAri,a@example.com,10\n",
        rules=[CleaningRuleCode.GENERATE_MISSING_COLUMN_NAMES],
    )

    assert result.cleaned_preview.columns == ["name", "email", "column_3"]
    assert result.after_summary.renamed_columns_count == 1


def test_normalize_missing_tokens() -> None:
    result = generate_cleaning_preview(
        filename="missing.csv",
        content_type="text/csv",
        content=b"name,item,amount\nAri,UNKNOWN,ERROR\nJustin,N/A,-\n",
        rules=[CleaningRuleCode.NORMALIZE_MISSING_TOKENS],
    )

    assert result.cleaned_preview.rows == [["Ari", "", ""], ["Justin", "", ""]]
    assert result.rule_effects[0].affected_rows == 2


def test_clean_numeric_values_for_numeric_like_columns() -> None:
    result = generate_cleaning_preview(
        filename="numbers.csv",
        content_type="text/csv",
        content=b"name,Quantity,Price Per Unit\nAri,\" 1,200 \",3.0\nJustin,ERROR,UNKNOWN\n",
        rules=[CleaningRuleCode.CLEAN_NUMERIC_VALUES],
    )

    assert result.cleaned_preview.rows == [["Ari", "1200", "3"], ["Justin", "", ""]]
    assert result.rule_effects[0].affected_columns == 2


def test_clean_date_values_for_date_like_columns() -> None:
    result = generate_cleaning_preview(
        filename="dates.csv",
        content_type="text/csv",
        content=b"name,Transaction Date\nAri,01/31/2026\nJustin,ERROR\nCase,not-a-date\n",
        rules=[CleaningRuleCode.CLEAN_DATE_VALUES],
    )

    assert result.cleaned_preview.rows == [["Ari", "2026-01-31"], ["Justin", ""], ["Case", ""]]
    assert result.rule_effects[0].affected_rows == 3


def test_standardize_category_text() -> None:
    result = generate_cleaning_preview(
        filename="categories.csv",
        content_type="text/csv",
        content=b"Item,Payment Method,Transaction ID\n coffee ,credit card,TXN_1\nTEA,DIGITAL WALLET,TXN_2\n",
        rules=[CleaningRuleCode.STANDARDIZE_CATEGORY_TEXT],
    )

    assert result.cleaned_preview.rows == [["Coffee", "Credit Card", "TXN_1"], ["Tea", "Digital Wallet", "TXN_2"]]
    assert result.rule_effects[0].affected_columns == 2


def test_recalculate_line_totals() -> None:
    result = generate_cleaning_preview(
        filename="sales.csv",
        content_type="text/csv",
        content=b"Quantity,Price Per Unit,Total Spent\n2,3.0,ERROR\n5,4.0,10.0\nUNKNOWN,4.0,20.0\n",
        rules=[CleaningRuleCode.CLEAN_NUMERIC_VALUES, CleaningRuleCode.RECALCULATE_LINE_TOTALS],
    )

    assert result.cleaned_preview.rows == [["2", "3", "6"], ["5", "4", "20"], ["", "4", ""]]
    assert result.rule_effects[1].affected_rows == 3


def test_multiple_rules_applied_together() -> None:
    result = generate_cleaning_preview(
        filename="combo.csv",
        content_type="text/csv",
        content=b"Customer Name,Empty\n Ari ,\n Ari ,\n,\n",
        rules=[
            CleaningRuleCode.TRIM_WHITESPACE,
            CleaningRuleCode.NORMALIZE_MISSING_TOKENS,
            CleaningRuleCode.REMOVE_EMPTY_ROWS,
            CleaningRuleCode.REMOVE_DUPLICATE_ROWS,
            CleaningRuleCode.DROP_EMPTY_COLUMNS,
            CleaningRuleCode.STANDARDIZE_COLUMN_NAMES,
        ],
    )

    assert result.cleaned_preview.columns == ["customer_name"]
    assert result.cleaned_preview.rows == [["Ari"]]
    assert result.after_summary.row_count == 1
    assert result.after_summary.removed_empty_rows_count == 1
    assert result.after_summary.removed_duplicate_rows_count == 1
    assert len(result.rule_effects) == 6


def test_cleaned_preview_is_bounded_to_twenty_rows() -> None:
    rows = "\n".join(f"Ari {index}" for index in range(30))
    result = generate_cleaning_preview(
        filename="many.csv",
        content_type="text/csv",
        content=f"name\n{rows}\n".encode(),
        rules=[CleaningRuleCode.TRIM_WHITESPACE],
    )

    assert len(result.cleaned_preview.rows) == 20


def test_tsv_cleaning_preview() -> None:
    result = generate_cleaning_preview(
        filename="sales.tsv",
        content_type="text/tab-separated-values",
        content=b"name\tamount\n Ari \t10\n",
        rules=[CleaningRuleCode.TRIM_WHITESPACE],
    )

    assert result.cleaned_preview.rows == [["Ari", "10"]]


def test_xlsx_selected_sheet_cleaning_preview() -> None:
    result = generate_cleaning_preview(
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

    assert result.cleaning_status == "preview_generated"
    assert result.selected_sheet_name == "Sales"
    assert result.cleaned_preview.columns == ["customer_name", "amount"]
    assert "excel_formatting_not_preserved" in {warning.code for warning in result.warnings}


def test_excel_without_sheet_name_requires_sheet_selection() -> None:
    result = generate_cleaning_preview(
        filename="workbook.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content=make_xlsx(),
        rules=[CleaningRuleCode.TRIM_WHITESPACE],
    )

    assert result.cleaning_status == "sheet_selection_required"
    assert result.next_step == "select_excel_sheet"


def test_unsupported_pdf_rejected() -> None:
    result = generate_cleaning_preview(
        filename="document.pdf",
        content_type="application/pdf",
        content=b"%PDF",
        rules=[CleaningRuleCode.TRIM_WHITESPACE],
    )

    assert result.cleaning_status == "rejected"


def test_empty_file_rejected() -> None:
    result = generate_cleaning_preview(
        filename="empty.csv",
        content_type="text/csv",
        content=b"",
        rules=[CleaningRuleCode.TRIM_WHITESPACE],
    )

    assert result.cleaning_status == "rejected"
    assert result.warnings[0].message == "File is empty. Upload a non-empty tabular file."
