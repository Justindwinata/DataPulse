from fastapi.testclient import TestClient

from datapulse_api.main import app


def test_cleaning_capabilities_returns_planned_formats_and_honest_status() -> None:
    client = TestClient(app)

    response = client.get("/cleaning/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["supported_input_formats"] == ["csv", "tsv", "txt", "xlsx", "xls"]
    assert "upload_validation" in payload["implemented_in_current_version"]
    assert "deterministic_cleaning_preview" in payload["implemented_in_current_version"]
    assert "workflow_templates" in payload["implemented_in_current_version"]
    assert "trim_whitespace" in payload["implemented_cleaning_rules"]
    assert "remove_duplicate_rows" in payload["implemented_cleaning_rules"]
    assert "promote_header_row" in payload["planned_cleaning_rules"]
    assert payload["export_strategy"] == "csv_first"
    assert "Original uploaded files are not stored" in payload["implementation_status"]
    assert "no_ai_cleaning" in payload["limitations"]
