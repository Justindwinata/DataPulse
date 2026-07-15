from fastapi.testclient import TestClient

from datapulse_api.main import app


def test_cors_allows_localhost_frontend_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/files/validate-upload",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_allows_127_frontend_origin_for_upload_response() -> None:
    client = TestClient(app)

    response = client.post(
        "/files/validate-upload",
        files={"file": ("demo.csv", b"name,total\nAri,100\n", "text/csv")},
        headers={"Origin": "http://127.0.0.1:5173"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert response.json()["validation_status"] == "accepted"
