import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from api.api_gateway.middleware.circuit_breaker import circuit_breaker, CircuitState, circuit_breaker_middleware

class DummyCallNext:
    def __init__(self, response: JSONResponse) -> None:
        self.response = response
    async def __call__(self, request: Request) -> JSONResponse:
        return self.response

@pytest.mark.asyncio
async def test_circuit_open() -> None:
    # Force the circuit to open for 'service'
    service_name = 'service'
    circuit = circuit_breaker.get_service_circuit(service_name)
    circuit['state'] = CircuitState.OPEN
    circuit['failure_count'] = 5
    circuit['last_failure_time'] = None
    request = MagicMock(spec=Request)
    request.url.path = f'/{service_name}/something'
    # Use a real JSONResponse for compatibility
    dummy_response = JSONResponse(content={})
    response = await circuit_breaker_middleware(request, DummyCallNext(dummy_response))
    assert response.status_code == 503
    assert b'unavailable' in response.body

@pytest.mark.asyncio
async def test_circuit_success() -> None:
    service_name = 'service2'
    circuit = circuit_breaker.get_service_circuit(service_name)
    circuit['state'] = CircuitState.CLOSED
    circuit['failure_count'] = 0
    request = MagicMock(spec=Request)
    request.url.path = f'/{service_name}/something'
    dummy_response = JSONResponse(content={}, status_code=200)
    call_next = DummyCallNext(dummy_response)
    response = await circuit_breaker_middleware(request, call_next)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_circuit_failure() -> None:
    # Simulate a failure in call_next to trigger circuit breaker record_failure
    service_name = 'service3'
    circuit = circuit_breaker.get_service_circuit(service_name)
    circuit['state'] = CircuitState.CLOSED
    circuit['failure_count'] = 0
    request = MagicMock(spec=Request)
    request.url.path = f'/{service_name}/something'
    async def failing_call_next(request: Request) -> JSONResponse:
        raise HTTPException(status_code=500, detail='fail')
    with pytest.raises(HTTPException):
        await circuit_breaker_middleware(request, failing_call_next) 