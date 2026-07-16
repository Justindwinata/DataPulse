from fastapi import APIRouter

from datapulse_api.models import CleaningRuleCode, CleaningRuleType, SupportedFileType

router = APIRouter(prefix="/cleaning", tags=["cleaning"])


@router.get("/capabilities")
def get_cleaning_capabilities() -> dict[str, list[str] | str]:
    return {
        "supported_input_formats": [file_type.value for file_type in SupportedFileType],
        "implemented_in_current_version": [
            "health_check",
            "domain_contracts",
            "capabilities_metadata",
            "upload_validation",
            "csv_tsv_txt_structure_detection",
            "excel_sheet_discovery",
            "excel_selected_sheet_preview",
            "data_quality_profiling",
            "deterministic_cleaning_preview",
            "cleaned_csv_export",
            "html_cleaning_report",
            "local_saved_sessions",
            "saved_session_report_replay",
            "saved_rule_restore",
            "workflow_templates",
        ],
        "implemented_cleaning_rules": [rule_code.value for rule_code in CleaningRuleCode],
        "planned_cleaning_rules": [
            rule_type.value
            for rule_type in CleaningRuleType
            if rule_type.value not in {rule_code.value for rule_code in CleaningRuleCode}
        ],
        "export_strategy": "csv_first",
        "implementation_status": (
            "DP-0013 local portfolio workflow is implemented: upload validation, structure "
            "detection, quality profiling, deterministic cleaning preview, CSV export, "
            "HTML reports, local saved sessions, rule restore, and workflow templates. "
            "Original uploaded files are not stored."
        ),
        "limitations": [
            "local_demo_application",
            "sample_based_preview_and_quality_profile",
            "metadata_only_saved_history",
            "excel_values_only_no_formatting_or_formulas",
            "no_authentication",
            "no_cloud_sync",
            "no_ai_cleaning",
        ],
    }
