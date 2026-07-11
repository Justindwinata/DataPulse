from fastapi.testclient import TestClient

from datapulse_api.main import app


def test_cleaning_capabilities_returns_planned_formats_and_honest_status() -> None:
    client = TestClient(app)

    response = client.get("/cleaning/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["supported_input_formats_planned"] == ["csv", "tsv", "txt", "xlsx", "xls"]
    assert payload["implemented_in_current_version"] == [
        "health_check",
        "domain_contracts",
        "capabilities_metadata",
    ]
    assert "trim_whitespace" in payload["planned_cleaning_rules"]
    assert "remove_duplicate_rows" in payload["planned_cleaning_rules"]
    assert payload["export_strategy"] == "csv_first"
    assert "not implemented yet" in payload["implementation_status"]
