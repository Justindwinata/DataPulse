from io import BytesIO
from typing import Any

from openpyxl import load_workbook

try:
    import xlrd
except ImportError:  # pragma: no cover - dependency is declared, fallback is defensive.
    xlrd = None

from datapulse_api.models import (
    ExcelSheetMetadata,
    ExcelWorkbookMetadata,
    StructureDetectionResult,
    StructureDetectionStatus,
    StructureNextStep,
    StructureWarning,
    StructureWarningSeverity,
)
from datapulse_api.services.file_validation import detect_extension, sanitize_filename

EXCEL_EXTENSIONS = frozenset({"xlsx", "xls"})
EXCEL_LIMITATION_WARNING = StructureWarning(
    code="excel_formatting_not_preserved",
    message=(
        "Excel formatting, formulas, merged cell behavior, charts, and pivot tables "
        "are not preserved in preview."
    ),
    severity=StructureWarningSeverity.INFO,
)


def detect_excel_workbook(
    *,
    filename: str,
    content_type: str | None,
    content: bytes,
) -> StructureDetectionResult:
    safe_filename = sanitize_filename(filename)
    extension = detect_extension(safe_filename) or "unknown"

    if extension not in EXCEL_EXTENSIONS:
        return _excel_rejected_result(
            filename=filename,
            safe_filename=safe_filename,
            extension=extension,
            content_type=content_type,
            file_size_bytes=len(content),
            code="file_not_excel",
            message="Excel sheet discovery supports XLSX and XLS files.",
            status=StructureDetectionStatus.REJECTED,
        )

    if not content:
        return _excel_rejected_result(
            filename=filename,
            safe_filename=safe_filename,
            extension=extension,
            content_type=content_type,
            file_size_bytes=0,
            code="empty_file",
            message="File is empty. Upload a non-empty Excel workbook.",
            status=StructureDetectionStatus.REJECTED,
        )

    try:
        workbook_metadata = (
            _discover_xlsx_workbook(content)
            if extension == "xlsx"
            else _discover_xls_workbook(content)
        )
    except Exception as error:
        return _excel_rejected_result(
            filename=filename,
            safe_filename=safe_filename,
            extension=extension,
            content_type=content_type,
            file_size_bytes=len(content),
            code="excel_workbook_unreadable",
            message="Excel workbook could not be read as a supported table-like workbook.",
            status=StructureDetectionStatus.REJECTED,
        )

    return StructureDetectionResult(
        original_filename=filename,
        safe_filename=safe_filename,
        detected_extension=extension,
        file_size_bytes=len(content),
        content_type=content_type,
        structure_status=StructureDetectionStatus.SHEET_SELECTION_REQUIRED,
        workbook=workbook_metadata,
        warnings=[EXCEL_LIMITATION_WARNING],
        next_step=StructureNextStep.SELECT_EXCEL_SHEET,
    )


def _discover_xlsx_workbook(content: bytes) -> ExcelWorkbookMetadata:
    workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
    sheet_names = workbook.sheetnames
    sheets = [
        ExcelSheetMetadata(
            sheet_name=worksheet.title,
            sheet_index=index,
            max_row=worksheet.max_row or 0,
            max_column=worksheet.max_column or 0,
            is_empty=_xlsx_sheet_is_empty(worksheet),
        )
        for index, worksheet in enumerate(workbook.worksheets)
    ]
    return ExcelWorkbookMetadata(
        workbook_type="xlsx",
        sheet_names=sheet_names,
        sheet_count=len(sheet_names),
        default_sheet_name=sheet_names[0],
        sheets=sheets,
    )


def _discover_xls_workbook(content: bytes) -> ExcelWorkbookMetadata:
    if xlrd is None:
        raise RuntimeError("xlrd is not installed")
    workbook = xlrd.open_workbook(file_contents=content, on_demand=True)
    sheet_names = workbook.sheet_names()
    sheets = [
        ExcelSheetMetadata(
            sheet_name=sheet_name,
            sheet_index=index,
            max_row=workbook.sheet_by_index(index).nrows,
            max_column=workbook.sheet_by_index(index).ncols,
            is_empty=workbook.sheet_by_index(index).nrows == 0
            or workbook.sheet_by_index(index).ncols == 0,
        )
        for index, sheet_name in enumerate(sheet_names)
    ]
    return ExcelWorkbookMetadata(
        workbook_type="xls",
        sheet_names=sheet_names,
        sheet_count=len(sheet_names),
        default_sheet_name=sheet_names[0],
        sheets=sheets,
    )


def _xlsx_sheet_is_empty(worksheet: Any) -> bool:
    for row in worksheet.iter_rows(min_row=1, max_row=1, values_only=True):
        return not any(cell is not None and str(cell).strip() for cell in row)
    return True


def _excel_rejected_result(
    *,
    filename: str,
    safe_filename: str,
    extension: str,
    content_type: str | None,
    file_size_bytes: int,
    code: str,
    message: str,
    status: StructureDetectionStatus,
) -> StructureDetectionResult:
    return StructureDetectionResult(
        original_filename=filename,
        safe_filename=safe_filename,
        detected_extension=extension,
        file_size_bytes=file_size_bytes,
        content_type=content_type,
        structure_status=status,
        warnings=[
            StructureWarning(
                code=code,
                message=message,
                severity=StructureWarningSeverity.ERROR,
            )
        ],
        next_step=StructureNextStep.UPLOAD_SUPPORTED_FILE,
    )
