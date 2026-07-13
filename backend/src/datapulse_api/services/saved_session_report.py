from typing import Any

from datapulse_api.models import (
    SavedCleaningSessionDetail,
    SavedSessionReportDocument,
    SavedSessionReportMetadata,
)


SAVED_REPORT_NOTICE = (
    "This report was generated from saved cleaning session metadata. "
    "Original uploaded files are not stored by DataPulse."
)

SAVED_REPORT_LIMITATIONS = [
    "This saved report is generated from stored metadata only.",
    "Original uploaded files are not stored by DataPulse.",
    "Saved reports cannot reprocess the original file or regenerate full cleaned CSV output.",
    "History is local SQLite only and is not cloud-synced.",
    "DataPulse uses deterministic, rule-based cleaning only.",
    "No AI or LLM cleaning is used.",
    "DataPulse does not guarantee perfect automatic cleaning.",
    "Excel formatting, formulas, merged cell behavior, charts, and pivot tables are not preserved.",
]


def build_saved_session_report(
    session: SavedCleaningSessionDetail,
) -> SavedSessionReportDocument:
    before_summary = _object(session.cleaning_summary.get("before_summary"))
    after_summary = _object(session.cleaning_summary.get("after_summary"))
    export_format = str(session.export_summary.get("format") or session.export_summary.get("export_format") or "CSV")

    return SavedSessionReportDocument(
        metadata=SavedSessionReportMetadata(
            session_id=session.id,
            source_filename=session.source_filename,
            detected_extension=session.detected_extension,
            selected_sheet_name=session.selected_sheet_name,
            session_created_at=session.created_at,
            session_updated_at=session.updated_at,
        ),
        metadata_notice=SAVED_REPORT_NOTICE,
        quality_score=_optional_int(session.quality_summary.get("quality_score")),
        total_issue_count=_non_negative_int(session.quality_summary.get("total_issue_count")),
        selected_rules=session.selected_rules,
        rows_before=_optional_int(before_summary.get("row_count")),
        rows_after=_optional_int(after_summary.get("row_count")),
        columns_before=_optional_int(before_summary.get("column_count")),
        columns_after=_optional_int(after_summary.get("column_count")),
        export_format=export_format,
        structure_summary=session.structure_summary,
        quality_summary=session.quality_summary,
        cleaning_summary=session.cleaning_summary,
        rule_effects=session.rule_effects,
        export_summary=session.export_summary,
        report_summary=session.report_summary,
        preview_snapshot=session.preview_snapshot,
        limitations=SAVED_REPORT_LIMITATIONS,
    )


def _object(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _non_negative_int(value: Any) -> int:
    parsed = _optional_int(value)
    return parsed if parsed is not None else 0
