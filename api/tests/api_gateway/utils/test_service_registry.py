import pytest
from api.api_gateway.utils.service_registry import service_registry, ServiceRegistry

@pytest.fixture
def registry() -> ServiceRegistry:
    return service_registry

def test_get_service_url_valid(registry: ServiceRegistry) -> None:
    url = registry.get_service_url('auth')
    assert url.startswith('http')

def test_get_service_url_invalid(registry: ServiceRegistry) -> None:
    with pytest.raises(ValueError):
        registry.get_service_url('notfound')

def test_get_service_for_path_valid(registry: ServiceRegistry) -> None:
    service = registry.get_service_for_path('/auth/login', 'POST')
    assert service['name'] == 'auth'
    assert service['url'].startswith('http')

def test_get_service_for_path_invalid(registry: ServiceRegistry) -> None:
    with pytest.raises(ValueError):
        registry.get_service_for_path('/unknown/path', 'GET')

def test_get_all_services(registry: ServiceRegistry) -> None:
    services = registry.get_all_services()
    assert isinstance(services, list)
    assert any(s['name'] == 'auth' for s in services) 