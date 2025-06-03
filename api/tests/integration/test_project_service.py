from fastapi.testclient import TestClient
from api.project_service.app.main import app
from unittest.mock import patch, MagicMock
from typing import Any

def _pass_auth_middleware(req: Any, call_next: Any) -> Any:
    return call_next(req)

def test_project_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("api.project_service.app.main.get_current_user", return_value="uid")
@patch("api.project_service.app.main.get_db", return_value=MagicMock())
@patch("api.project_service.app.services.project_service.ProjectService.create_project")
@patch("api.project_service.app.main.auth_middleware", new=_pass_auth_middleware)
def test_create_project(mock_create_project: MagicMock, mock_db: Any, mock_user: Any) -> None:
    client = TestClient(app)
    mock_create_project.return_value = {
        "id": "pid",
        "name": "TestProject",
        "status": "planning",
        "owner_id": "uid",
        "created_at": "2025-01-01T00:00:00Z"
    }
    payload = {
        "name": "TestProject"
    }
    headers = {"Authorization": "Bearer testtoken"}
    response = client.post("/projects", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestProject" 