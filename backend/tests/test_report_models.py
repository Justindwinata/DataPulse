from datapulse_api.models import (
    CleaningReportDocument,
    CleaningReportMetadata,
    CleaningRuleCode,
    CleaningStatus,
    CleaningSummaryAfter,
    CleaningSummaryBefore,
    DataQualityResult,
    QualityNextStep,
    QualityStatus,
    ReportExportMetadata,
    StructureDetectionResult,
    StructureDetectionStatus,
    StructureNextStep,
    CleaningPreviewResult,
)


def test_cleaning_report_document_accepts_composed_workflow_outputs() -> None:
    structure = StructureDetectionResult(
        original_filename="sales.csv",
        safe_filename="sales.csv",
        detected_extension="csv",
        file_size_bytes=20,
        content_type="text/csv",
        structure_status=StructureDetectionStatus.DETECTED,
        column_names=["name"],
        detected_column_count=1,
        next_step=StructureNextStep.QUALITY_ISSUE_DETECTION,
    )
    quality = DataQualityResult(
        quality_status=QualityStatus.PROFILED,
        original_filename="sales.csv",
        safe_filename="sales.csv",
        detected_extension="csv",
        next_step=QualityNextStep.CLEANING_RULES,
    )
    cleaning = CleaningPreviewResult(
        cleaning_status=CleaningStatus.PREVIEW_GENERATED,
        original_filename="sales.csv",
        safe_filename="sales.csv",
        detected_extension="csv",
        applied_rules=[CleaningRuleCode.TRIM_WHITESPACE],
        before_summary=CleaningSummaryBefore(row_count=1, column_count=1),
        after_summary=CleaningSummaryAfter(row_count=1, column_count=1),
        next_step="download_cleaned_csv",
    )

    report = CleaningReportDocument(
        metadata=CleaningReportMetadata(
            source_filename="sales.csv",
            detected_extension="csv",
            selected_rules=[CleaningRuleCode.TRIM_WHITESPACE],
        ),
        structure=structure,
        quality=quality,
        cleaning=cleaning,
        export=ReportExportMetadata(filename="sales_cleaned.csv", content_type="text/csv"),
        limitations=["Deterministic rule-based cleaning."],
    )

    assert report.metadata.title == "DataPulse Cleaning Report"
    assert report.export.csv_first_strategy is True
    assert report.metadata.selected_rules == [CleaningRuleCode.TRIM_WHITESPACE]
