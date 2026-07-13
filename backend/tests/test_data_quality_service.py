from io import BytesIO

from openpyxl import Workbook

from datapulse_api.services.data_quality import detect_data_quality


def issue_codes(payload) -> set[str]:
    return {issue.code for issue in payload.issues}


def column_by_name(payload, name: str):
    return next(column for column in payload.columns if column.column_name == name)


def make_xlsx() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sales"
    worksheet.append(["Customer", "Amount", "Email"])
    worksheet.append(["Ari", 1200, "ari@example.com"])
    worksheet.append(["Justin", None, " justin@example.com "])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_clean_csv_produces_profile_with_no_warning_or_critical_issues() -> None:
    result = detect_data_quality(
        filename="people.csv",
        content_type="text/csv",
        content=b"name,city\nAri,Jakarta\nJustin,Bandung\n",
    )

    assert result.quality_status == "profiled"
    assert result.detected_column_count == 2
    assert result.severity_counts.warning == 0
    assert result.severity_counts.critical == 0
    assert result.quality_score == 100


def test_detects_missing_values_empty_rows_empty_columns_and_high_missing_columns() -> None:
    result = detect_data_quality(
        filename="missing.csv",
        content_type="text/csv",
        content=b"name,email,notes\nAri,,\n,,\nJustin,justin@example.com,\n",
    )

    codes = issue_codes(result)
    assert "missing_values" in codes
    assert "empty_rows" in codes
    assert "empty_columns" in codes
    assert "high_missing_column" in codes
    assert column_by_name(result, "notes").inferred_type == "empty"


def test_detects_duplicate_rows() -> None:
    result = detect_data_quality(
        filename="duplicates.csv",
        content_type="text/csv",
        content=b"name,city\nAri,Jakarta\nAri,Jakarta\n",
    )

    assert "duplicate_rows" in issue_codes(result)


def test_detects_duplicate_and_missing_column_names() -> None:
    result = detect_data_quality(
        filename="headers.csv",
        content_type="text/csv",
        content=b"name,name,\nAri,Jakarta,10\n",
    )

    codes = issue_codes(result)
    assert "duplicate_column_names" in codes
    assert "missing_column_names" in codes


def test_detects_whitespace_and_messy_column_names() -> None:
    result = detect_data_quality(
        filename="messy.csv",
        content_type="text/csv",
        content=b"Full Name!,city\n Ari ,Jakarta\n",
    )

    assert "messy_column_names" in issue_codes(result)
    assert "leading_trailing_whitespace" in issue_codes(result)


def test_detects_mixed_numeric_and_date_text_patterns() -> None:
    result = detect_data_quality(
        filename="types.csv",
        content_type="text/csv",
        content=(
            b"name,amount,order_date,mixed\n"
            b"Ari,1200,2026-01-01,10\n"
            b"Justin,1500,2026-01-02,unknown\n"
        ),
    )

    codes = issue_codes(result)
    assert "numeric_values_as_text" in codes
    assert "date_values_as_text" in codes
    assert "mixed_type_values" in codes
    assert column_by_name(result, "amount").inferred_type == "number"
    assert column_by_name(result, "order_date").inferred_type == "date"
    assert column_by_name(result, "mixed").inferred_type == "mixed"


def test_detects_inconsistent_row_widths_from_structure_warnings() -> None:
    result = detect_data_quality(
        filename="widths.csv",
        content_type="text/csv",
        content=b"name,amount\nAri,10\nJustin,20,extra\n",
    )

    assert "inconsistent_row_widths" in issue_codes(result)


def test_profiles_selected_excel_sheet() -> None:
    result = detect_data_quality(
        filename="workbook.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content=make_xlsx(),
        sheet_name="Sales",
    )

    codes = issue_codes(result)
    assert result.quality_status == "profiled"
    assert result.selected_sheet_name == "Sales"
    assert "missing_values" in codes
    assert "numeric_values_as_text" in codes
    assert "leading_trailing_whitespace" in codes


def test_excel_without_sheet_name_requires_sheet_selection() -> None:
    result = detect_data_quality(
        filename="workbook.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content=make_xlsx(),
    )

    assert result.quality_status == "sheet_selection_required"
    assert result.next_step == "select_excel_sheet"
    assert result.messages == ["Select an Excel sheet before running data quality profiling."]


def test_unsupported_pdf_is_rejected() -> None:
    result = detect_data_quality(
        filename="document.pdf",
        content_type="application/pdf",
        content=b"%PDF",
    )

    assert result.quality_status == "rejected"
    assert result.next_step == "upload_supported_file"


def test_empty_file_is_rejected() -> None:
    result = detect_data_quality(filename="empty.csv", content_type="text/csv", content=b"")

    assert result.quality_status == "rejected"
    assert result.messages == ["File is empty. Upload a non-empty tabular file."]


def test_quality_score_is_deterministic() -> None:
    content = b"name,amount\nAri,\nAri,\n"

    first = detect_data_quality(filename="score.csv", content_type="text/csv", content=content)
    second = detect_data_quality(filename="score.csv", content_type="text/csv", content=content)

    assert first.quality_score == second.quality_score
    assert first.severity_counts == second.severity_counts
