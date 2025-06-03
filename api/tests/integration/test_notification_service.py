from fastapi.testclient import TestClient
from api.notification_service.app.main import app
from unittest.mock import patch, MagicMock
from typing import Any

def _pass_auth_middleware(req: Any, call_next: Any) -> Any:
    return call_next(req)

def test_notification_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("api.notification_service.app.main.get_current_user", return_value="uid")
@patch("api.notification_service.app.main.get_db", return_value=MagicMock())
@patch("api.notification_service.app.services.notification_service.NotificationService.create_notification")
@patch("api.notification_service.app.main.auth_middleware", new=_pass_auth_middleware)
def test_create_notification(mock_create_notification: MagicMock, mock_db: Any, mock_user: Any) -> None:
    client = TestClient(app)
    mock_create_notification.return_value = {
        "id": "nid",
        "user_id": "uid",
        "type": "system",
        "title": "TestNotif",
        "message": "Hello",
        "priority": "normal",
        "channels": ["in_app"],
        "created_at": "2025-01-01T00:00:00Z"
    }
    payload = {
        "user_id": "uid",
        "type": "system",
        "title": "TestNotif",
        "message": "Hello"
    }
    headers = {"Authorization": "Bearer testtoken"}
    response = client.post("/notifications", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "TestNotif" 