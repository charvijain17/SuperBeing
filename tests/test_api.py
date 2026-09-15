from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health_endpoint():
    assert client.get("/health").status_code == 200
def test_docs_are_available():
    assert client.get("/docs").status_code == 200
def test_chat_reports_missing_provider_key():
    response=client.post("/chat", json={"provider":"openai","prompt":"Hello"})
    assert response.status_code == 503
