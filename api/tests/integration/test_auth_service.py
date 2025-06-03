from fastapi.testclient import TestClient
from api.auth_service.app.main import app
from unittest.mock import patch, MagicMock

def test_auth_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("api.auth_service.app.services.auth_service.AuthService.register")
def test_register_user(mock_register: MagicMock) -> None:
    client = TestClient(app)
    # Simula el retorno de un TokenDTO
    mock_register.return_value = {
        "access_token": "token",
        "refresh_token": "refresh",
        "token_type": "bearer",
        "expires_at": "2025-01-01T00:00:00Z"
    }
    payload = {
        "email": "test@example.com",
        "password": "12345678",
        "full_name": "Test User",
        "company_name": "TestCo"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data 