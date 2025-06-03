from fastapi.testclient import TestClient
from api.external_tools_service.app.main import app
from unittest.mock import patch, MagicMock
from typing import Any

def _pass_auth_middleware(req: Any, call_next: Any) -> Any:
    return call_next(req)

def test_external_tools_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("api.external_tools_service.app.main.get_current_user", return_value="uid")
@patch("api.external_tools_service.app.main.get_db", return_value=MagicMock())
@patch("api.external_tools_service.app.services.external_tools_service.ExternalToolsService.get_oauth_providers")
@patch("api.external_tools_service.app.main.auth_middleware", new=_pass_auth_middleware)
def test_get_oauth_providers(mock_get_oauth_providers: MagicMock, mock_db: Any, mock_user: Any) -> None:
    client = TestClient(app)
    mock_get_oauth_providers.return_value = [
        {
            "id": "prov1",
            "name": "GitHub",
            "type": "github",
            "auth_url": "https://auth/",
            "token_url": "https://token/",
            "scope": "repo",
            "client_id": "cid",
            "redirect_uri": "https://cb/"
        }
    ]
    headers = {"Authorization": "Bearer testtoken"}
    response = client.get("/oauth/providers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "GitHub" 