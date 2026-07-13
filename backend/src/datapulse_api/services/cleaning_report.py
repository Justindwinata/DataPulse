from collections.abc import Iterable

from datapulse_api.models import (
    CleaningReportDocument,
    CleaningReportMetadata,
    CleaningRuleCode,
    ReportExportMetadata,
    StructureDetectionResult,
    StructureDetectionStatus,
)
from datapulse_api.services.cleaned_csv_export import (
    CleanedCsvExportError,
    export_cleaned_csv,
)
from datapulse_api.services.cleaning_engine import generate_cleaning_preview
from datapulse_api.services.csv_structure_detection import (
    CSV_LIKE_EXTENSIONS,
    EXCEL_EXTENSIONS,
    detect_csv_like_structure,
)
from datapulse_api.services.data_quality import detect_data_quality
from datapulse_api.services.excel_structure_detection import (
    detect_excel_sheet_preview,
    detect_excel_workbook,
)
from datapulse_api.services.file_validation import detect_extension, sanitize_filename


REPORT_LIMITATIONS = [
    "DataPulse uses deterministic, rule-based cleaning only.",
    "No AI or LLM cleaning is used in this report.",
    "DataPulse does not guarantee perfect automatic cleaning.",
    "The report is generated from the uploaded data and selected rules.",
    "The original uploaded file is not modified.",
    "Excel formatting, formulas, merged cell behavior, charts, and pivot tables are not preserved.",
]


def build_cleaning_report(
    *,
    filename: str,
    content_type: str | None,
    content: bytes,
    rules: Iterable[CleaningRuleCode],
    sheet_name: str | None = None,
) -> CleaningReportDocument:
    safe_filename = sanitize_filename(filename)
    extension = detect_extension(safe_filename) or "unknown"
    selected_rules = list(rules)
    structure = _detect_report_structure(
        filename=filename,
        content_type=content_type,
        content=content,
        extension=extension,
        sheet_name=sheet_name,
    )

    if structure.structure_status != StructureDetectionStatus.DETECTED:
        _raise_from_structure(structure)

    quality = detect_data_quality(
        filename=filename,
        content_type=content_type,
        content=content,
        sheet_name=sheet_name,
    )
    cleaning = generate_cleaning_preview(
        filename=filename,
        content_type=content_type,
        content=content,
        rules=selected_rules,
        sheet_name=sheet_name,
    )
    exported = export_cleaned_csv(
        filename=filename,
        content_type=content_type,
        content=content,
        rules=selected_rules,
        sheet_name=sheet_name,
    )

    return CleaningReportDocument(
        metadata=CleaningReportMetadata(
            source_filename=structure.safe_filename,
            detected_extension=extension,
            selected_sheet_name=structure.selected_sheet_name,
            selected_rules=selected_rules,
        ),
        structure=structure,
        quality=quality,
        cleaning=cleaning,
        export=ReportExportMetadata(
            filename=exported.filename,
            content_type=exported.content_type,
        ),
        limitations=REPORT_LIMITATIONS,
    )


def _detect_report_structure(
    *,
    filename: str,
    content_type: str | None,
    content: bytes,
    extension: str,
    sheet_name: str | None,
) -> StructureDetectionResult:
    if extension in CSV_LIKE_EXTENSIONS:
        return detect_csv_like_structure(
            filename=filename,
            content_type=content_type,
            content=content,
        )
    if extension in EXCEL_EXTENSIONS:
        if not sheet_name:
            workbook = detect_excel_workbook(
                filename=filename,
                content_type=content_type,
                content=content,
            )
            if workbook.structure_status == StructureDetectionStatus.SHEET_SELECTION_REQUIRED:
                raise CleanedCsvExportError(
                    "sheet_selection_required",
                    "Select an Excel sheet before generating an HTML cleaning report.",
                )
            return workbook
        return detect_excel_sheet_preview(
            filename=filename,
            content_type=content_type,
            content=content,
            sheet_name=sheet_name,
        )
    return detect_csv_like_structure(
        filename=filename,
        content_type=content_type,
        content=content,
    )


def _raise_from_structure(structure: StructureDetectionResult) -> None:
    if structure.file_size_bytes == 0:
        raise CleanedCsvExportError("empty_file", "File is empty. Upload a non-empty tabular file.")
    warning = structure.warnings[0] if structure.warnings else None
    raise CleanedCsvExportError(
        warning.code if warning else "report_rejected",
        warning.message if warning else "File cannot be used to generate an HTML cleaning report.",
    )
