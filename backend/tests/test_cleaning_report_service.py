from io import BytesIO

import pytest
from openpyxl import Workbook

from datapulse_api.models import CleaningRuleCode
from datapulse_api.services.cleaned_csv_export import CleanedCsvExportError
from datapulse_api.services.cleaning_report import build_cleaning_report


def make_xlsx() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sales"
    worksheet.append(["Customer Name", "Amount", "Empty"])
    worksheet.append([" Ari ", 1200, None])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_build_cleaning_report_for_csv_composes_workflow_outputs() -> None:
    report = build_cleaning_report(
        filename="messy.csv",
        content_type="text/csv",
        content=b"Customer Name,Amount\n Ari ,1200\n,\n",
        rules=[
            CleaningRuleCode.TRIM_WHITESPACE,
            CleaningRuleCode.REMOVE_EMPTY_ROWS,
            CleaningRuleCode.STANDARDIZE_COLUMN_NAMES,
        ],
    )

    assert report.metadata.source_filename == "messy.csv"
    assert report.structure.structure_status == "detected"
    assert report.quality.quality_status == "profiled"
    assert report.cleaning.cleaning_status == "preview_generated"
    assert report.export.filename == "messy_cleaned.csv"
    assert report.cleaning.cleaned_preview.columns == ["customer_name", "amount"]


def test_build_cleaning_report_includes_advanced_rule_effects() -> None:
    report = build_cleaning_report(
        filename="dirty-cafe.csv",
        content_type="text/csv",
        content=(
            b"Transaction ID,Item,Quantity,Price Per Unit,Total Spent,Transaction Date\n"
            b"TXN_1,UNKNOWN,2,3.0,ERROR,01/31/2026\n"
        ),
        rules=[
            CleaningRuleCode.NORMALIZE_MISSING_TOKENS,
            CleaningRuleCode.CLEAN_NUMERIC_VALUES,
            CleaningRuleCode.CLEAN_DATE_VALUES,
            CleaningRuleCode.RECALCULATE_LINE_TOTALS,
        ],
    )

    labels = {effect.label for effect in report.cleaning.rule_effects}
    assert "Normalize missing tokens" in labels
    assert "Clean numeric values" in labels
    assert "Clean date values" in labels
    assert "Recalculate line totals" in labels
    assert report.cleaning.cleaned_preview.rows == [["TXN_1", "", "2", "3", "6", "2026-01-31"]]


def test_build_cleaning_report_for_xlsx_selected_sheet() -> None:
    report = build_cleaning_report(
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

    assert report.metadata.selected_sheet_name == "Sales"
    assert report.structure.selected_sheet_name == "Sales"
    assert report.export.filename == "workbook_cleaned.csv"
    assert "Excel formatting" in " ".join(report.limitations)


def test_build_cleaning_report_for_excel_without_sheet_requires_selection() -> None:
    with pytest.raises(CleanedCsvExportError) as error:
        build_cleaning_report(
            filename="workbook.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            content=make_xlsx(),
            rules=[CleaningRuleCode.TRIM_WHITESPACE],
        )

    assert error.value.code == "sheet_selection_required"


def test_build_cleaning_report_rejects_empty_file() -> None:
    with pytest.raises(CleanedCsvExportError) as error:
        build_cleaning_report(
            filename="empty.csv",
            content_type="text/csv",
            content=b"",
            rules=[],
        )

    assert error.value.code == "empty_file"
