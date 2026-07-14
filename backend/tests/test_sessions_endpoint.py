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


def test_saved_session_report_returns_html_from_metadata(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    create_response = client.post("/sessions", json=session_payload())
    session_id = create_response.json()["id"]

    response = client.get(f"/sessions/{session_id}/report.html")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "DataPulse Saved Cleaning Session Report" in response.text
    assert "messy.csv" in response.text
    assert "This report was generated from saved cleaning session metadata" in response.text
    assert "trim_whitespace" in response.text
    assert "Quality score" in response.text
    assert "Original uploaded files are not stored by DataPulse" in response.text
    app.dependency_overrides.clear()


def test_saved_session_report_escapes_stored_values(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    payload = session_payload()
    payload["source_filename"] = '<script>alert("file")</script>.csv'
    payload["structure_summary"] = {
        "detected_column_count": 1,
        "warnings": [{"message": "<img src=x onerror=alert(1)>"}],
    }
    payload["quality_summary"] = {
        "quality_score": 50,
        "total_issue_count": 1,
        "issues": [{"title": "<b>Unsafe</b>", "message": "<script>alert(1)</script>"}],
    }
    payload["preview_snapshot"] = {
        "columns": ["<script>column</script>"],
        "rows": [["<img src=x onerror=alert(1)>"]],
    }
    session_id = client.post("/sessions", json=payload).json()["id"]

    response = client.get(f"/sessions/{session_id}/report.html")

    assert response.status_code == 200
    assert "<script>alert" not in response.text
    assert "<img src=x" not in response.text
    assert "&lt;script&gt;alert" in response.text
    assert "&lt;img src=x" in response.text
    app.dependency_overrides.clear()


def test_saved_session_report_missing_session_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/sessions/999/report.html")

    assert response.status_code == 404
    assert response.json()["detail"] == "Saved cleaning session not found."
    app.dependency_overrides.clear()


def test_get_saved_session_rules_returns_metadata_only_notes(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    create_response = client.post("/sessions", json=session_payload())
    session_id = create_response.json()["id"]

    response = client.get(f"/sessions/{session_id}/rules")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["source_filename"] == "messy.csv"
    assert payload["selected_rules"] == ["trim_whitespace"]
    assert payload["selected_rules_count"] == 1
    assert "Original uploaded files are not stored" in payload["original_file_storage_note"]
    assert "Upload a new file" in payload["new_upload_required_note"]
    app.dependency_overrides.clear()


def test_get_saved_session_rules_missing_session_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/sessions/999/rules")

    assert response.status_code == 404
    assert response.json()["detail"] == "Saved cleaning session not found."
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
