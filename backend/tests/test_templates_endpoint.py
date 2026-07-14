from pathlib import Path

from fastapi.testclient import TestClient

from datapulse_api.api.sessions import get_session_repository as get_sessions_api_repository
from datapulse_api.api.templates import (
    get_session_repository as get_templates_session_repository,
    get_template_repository,
)
from datapulse_api.main import app
from datapulse_api.services.session_repository import CleaningSessionRepository
from datapulse_api.services.template_repository import WorkflowTemplateRepository
from tests.test_sessions_endpoint import session_payload


def template_payload() -> dict:
    return {
        "name": "Sales cleanup",
        "description": "Reusable rules for sales exports",
        "selected_rules": ["trim_whitespace", "remove_empty_rows"],
        "source_filename": "messy.csv",
    }


def make_client(tmp_path: Path) -> TestClient:
    database_path = tmp_path / "templates-api.sqlite3"
    template_repository = WorkflowTemplateRepository(database_path)
    session_repository = CleaningSessionRepository(database_path)
    app.dependency_overrides[get_template_repository] = lambda: template_repository
    app.dependency_overrides[get_templates_session_repository] = lambda: session_repository
    app.dependency_overrides[get_sessions_api_repository] = lambda: session_repository
    return TestClient(app)


def test_create_list_get_update_and_delete_template(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    create_response = client.post("/templates", json=template_payload())
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Sales cleanup"
    assert created["selected_rules"] == ["trim_whitespace", "remove_empty_rows"]
    assert "Original files are not stored" in created["storage_note"]

    list_response = client.get("/templates")
    assert list_response.status_code == 200
    assert list_response.json()["total_count"] == 1

    detail_response = client.get(f"/templates/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["selected_rules_count"] == 2

    update_response = client.patch(
        f"/templates/{created['id']}",
        json={
            "name": "Updated cleanup",
            "description": "",
            "selected_rules": ["drop_empty_columns"],
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated cleanup"
    assert update_response.json()["description"] is None
    assert update_response.json()["selected_rules"] == ["drop_empty_columns"]

    delete_response = client.delete(f"/templates/{created['id']}")
    assert delete_response.status_code == 204
    assert client.get("/templates").json()["total_count"] == 0
    app.dependency_overrides.clear()


def test_create_template_rejects_empty_rules(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    payload = template_payload()
    payload["selected_rules"] = []

    response = client.post("/templates", json=payload)

    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_create_template_rejects_invalid_rule_code(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    payload = template_payload()
    payload["selected_rules"] = ["convert_numeric_columns"]

    response = client.post("/templates", json=payload)

    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_missing_template_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    assert client.get("/templates/999").status_code == 404
    assert client.patch("/templates/999", json={"name": "Missing"}).status_code == 404
    assert client.delete("/templates/999").status_code == 404
    app.dependency_overrides.clear()


def test_create_template_from_saved_session(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    session_response = client.post("/sessions", json=session_payload())
    session_id = session_response.json()["id"]

    response = client.post(
        f"/templates/from-session/{session_id}",
        json={
            "name": "From saved session",
            "description": "Session rules",
            "selected_rules": ["drop_empty_columns"],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["source_session_id"] == session_id
    assert payload["source_filename"] == "messy.csv"
    assert payload["selected_rules"] == ["trim_whitespace"]
    app.dependency_overrides.clear()


def test_create_template_from_missing_session_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/templates/from-session/999",
        json=template_payload(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Saved cleaning session not found."
    app.dependency_overrides.clear()
