from pathlib import Path

from fastapi.testclient import TestClient

from datapulse_api.api.sessions import get_session_repository
from datapulse_api.main import app
from datapulse_api.services.session_repository import CleaningSessionRepository


def session_payload() -> dict:
    return {
        "source_filename": "messy.csv",
        "detected_extension": "csv",
        "content_type": "text/csv",
        "file_size_bytes": 42,
        "structure_summary": {"detected_column_count": 2},
        "quality_summary": {"quality_score": 91, "total_issue_count": 2},
        "selected_rules": ["trim_whitespace"],
        "cleaning_summary": {
            "before_summary": {"row_count": 3, "column_count": 2},
            "after_summary": {"row_count": 2, "column_count": 2},
        },
        "rule_effects": [{"rule": "trim_whitespace", "status": "applied"}],
        "export_summary": {"format": "CSV", "filename": "messy_cleaned.csv"},
        "report_summary": {"format": "HTML"},
        "preview_snapshot": {"columns": ["name"], "rows": [["Ari"]]},
    }


def make_client(tmp_path: Path) -> TestClient:
    repository = CleaningSessionRepository(tmp_path / "api-history.sqlite3")
    app.dependency_overrides[get_session_repository] = lambda: repository
    return TestClient(app)


def test_create_list_get_and_delete_session(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    create_response = client.post("/sessions", json=session_payload())
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["source_filename"] == "messy.csv"
    assert created["storage_note"].startswith("Original uploaded files are not stored")

    list_response = client.get("/sessions")
    assert list_response.status_code == 200
    assert list_response.json()["total_count"] == 1
    assert list_response.json()["sessions"][0]["selected_rules_count"] == 1

    detail_response = client.get(f"/sessions/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["preview_snapshot"]["rows"] == [["Ari"]]

    delete_response = client.delete(f"/sessions/{created['id']}")
    assert delete_response.status_code == 204
    assert client.get("/sessions").json()["total_count"] == 0
    app.dependency_overrides.clear()


def test_create_session_rejects_invalid_payload(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    payload = session_payload()
    payload["selected_rules"] = []

    response = client.post("/sessions", json=payload)

    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_get_missing_session_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/sessions/999")

    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_delete_missing_session_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.delete("/sessions/999")

    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_sessions_do_not_accept_uploaded_files(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/sessions",
        files={"file": ("messy.csv", b"name\nAri\n", "text/csv")},
    )

    assert response.status_code == 422
    app.dependency_overrides.clear()
