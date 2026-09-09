from io import BytesIO

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_process_rejects_unknown_file():
    response = client.post(
        "/api/process",
        files={"files": ("notes.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 422

