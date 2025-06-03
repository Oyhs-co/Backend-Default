from fastapi.testclient import TestClient
from api.document_service.app.main import app
from unittest.mock import patch, MagicMock
from typing import Any

def _pass_auth_middleware(req: Any, call_next: Any) -> Any:
    return call_next(req)

def test_document_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("api.document_service.app.main.get_current_user", return_value="uid")
@patch("api.document_service.app.main.get_db", return_value=MagicMock())
@patch("api.document_service.app.services.document_service.DocumentService.create_document")
@patch("api.document_service.app.main.auth_middleware", new=_pass_auth_middleware)
def test_create_document(mock_create_document: MagicMock, mock_db: Any, mock_user: Any) -> None:
    client = TestClient(app)
    mock_create_document.return_value = {
        "id": "docid",
        "name": "TestDoc",
        "project_id": "pid",
        "type": "file",
        "version": 1,
        "creator_id": "uid",
        "created_at": "2025-01-01T00:00:00Z"
    }
    payload = {
        "name": "TestDoc",
        "project_id": "pid",
        "type": "file"
    }
    headers = {"Authorization": "Bearer testtoken"}
    response = client.post("/documents", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestDoc" 