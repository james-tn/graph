from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("app.services.graphrag_service.graphrag_service.save_file", new_callable=AsyncMock)
def test_upload_file(mock_save):
    mock_save.return_value = "path/to/file"
    files = {"file": ("test.txt", b"content", "text/plain")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    assert response.json()["message"] == "File test.txt uploaded successfully"

@patch("app.services.graphrag_service.graphrag_service.run_ingestion", new_callable=AsyncMock)
def test_index(mock_ingest):
    response = client.post("/api/index")
    assert response.status_code == 200
    assert response.json()["message"] == "Ingestion completed successfully"

@patch("app.services.graphrag_service.graphrag_service.query", new_callable=AsyncMock)
def test_query(mock_query):
    mock_query.return_value = {"answer": "test answer", "sources": []}
    response = client.post("/api/query", json={"query": "test"})
    assert response.status_code == 200
    assert response.json()["answer"] == "test answer"
