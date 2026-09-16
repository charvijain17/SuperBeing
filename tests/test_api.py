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


def test_versioned_day_one_chat_endpoint_still_works():
    response=client.post("/api/v1/chat", json={"provider":"openai","prompt":"Hello"})
    assert response.status_code == 503


def test_workflow_reports_no_configured_provider():
    response=client.post("/api/v1/workflow", json={"message":"Compare Java and Python.", "provider":"auto"})
    assert response.status_code == 503
    assert "No LLM provider is configured" in response.json()["detail"]
