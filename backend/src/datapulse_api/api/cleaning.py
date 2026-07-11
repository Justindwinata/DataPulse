from fastapi import APIRouter

from datapulse_api.models import CleaningRuleType, SupportedFileType

router = APIRouter(prefix="/cleaning", tags=["cleaning"])


@router.get("/capabilities")
def get_cleaning_capabilities() -> dict[str, list[str] | str]:
    return {
        "supported_input_formats_planned": [file_type.value for file_type in SupportedFileType],
        "implemented_in_current_version": [
            "health_check",
            "domain_contracts",
            "capabilities_metadata",
        ],
        "planned_cleaning_rules": [rule_type.value for rule_type in CleaningRuleType],
        "export_strategy": "csv_first",
        "implementation_status": (
            "DP-0001 defines product foundations only. File upload, parsing, cleaning, "
            "export, reports, and saved history are not implemented yet."
        ),
    }
