from fastapi.testclient import TestClient
from api.api_gateway.main import app
from unittest.mock import patch, MagicMock
from typing import Any

client = TestClient(app)

def _pass_auth_middleware(req: Any, call_next: Any) -> Any:
    return call_next(req)

def _pass_circuit_breaker_middleware(req: Any, call_next: Any) -> Any:
    return call_next(req)

@patch("api.api_gateway.main.auth_middleware", new=_pass_auth_middleware)
@patch("api.api_gateway.main.circuit_breaker_middleware", new=_pass_circuit_breaker_middleware)
def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("api.api_gateway.main.auth_middleware", new=_pass_auth_middleware)
@patch("api.api_gateway.main.circuit_breaker_middleware", new=_pass_circuit_breaker_middleware)
@patch("api.api_gateway.utils.service_registry.service_registry.get_all_services", return_value=[{"name": "test", "url": "http://localhost"}])
def test_get_services(mock_services: MagicMock) -> None:
    response = client.get("/services")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 