import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, status
from api.api_gateway.middleware.auth_middleware import auth_middleware
from typing import Any

class DummyCallNext:
    def __init__(self, response: Any) -> None:
        self.response = response
    async def __call__(self, request: Request) -> Any:
        return self.response

@pytest.mark.asyncio
async def test_skip_auth():
    request = MagicMock(spec=Request)
    request.url.path = '/health'
    dummy_response = MagicMock()
    call_next = DummyCallNext(dummy_response)
    response = await auth_middleware(request, call_next)
    assert response == dummy_response

@pytest.mark.asyncio
async def test_valid_token():
    request = MagicMock(spec=Request)
    request.url.path = '/protected'
    request.headers = {'Authorization': 'Bearer validtoken'}
    dummy_response = MagicMock()
    call_next = DummyCallNext(dummy_response)
    with patch('api.api_gateway.middleware.auth_middleware._validate_token', new=AsyncMock(return_value='user123')):
        response = await auth_middleware(request, call_next)
        assert response == dummy_response
        assert request.state.user_id == 'user123'

@pytest.mark.asyncio
async def test_no_token():
    request = MagicMock(spec=Request)
    request.url.path = '/protected'
    request.headers = {}
    call_next = DummyCallNext(MagicMock())
    response = await auth_middleware(request, call_next)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.body is not None

@pytest.mark.asyncio
async def test_invalid_token():
    request = MagicMock(spec=Request)
    request.url.path = '/protected'
    request.headers = {'Authorization': 'Bearer invalidtoken'}
    call_next = DummyCallNext(MagicMock())
    with patch('api.api_gateway.middleware.auth_middleware._validate_token', new=AsyncMock(side_effect=Exception('fail'))):
        response = await auth_middleware(request, call_next)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.body is not None 