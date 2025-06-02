import asyncio
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict

import httpx
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class CircuitState(str, Enum):
    """Enum for circuit breaker states"""

    CLOSED = "closed"  # Normal operation, requests are allowed
    OPEN = "open"  # Circuit is open, requests are blocked
    HALF_OPEN = "half_open"  # Testing if service is back online


class CircuitBreaker:
    """Circuit breaker for protecting services"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        timeout: float = 5.0,
    ):
        """
        Initialize CircuitBreaker.

        Args:
            failure_threshold (int, optional): Number of failures before opening circuit. Defaults to 5.
            recovery_timeout (int, optional): Seconds to wait before trying again. Defaults to 30.
            timeout (float, optional): Request timeout in seconds. Defaults to 5.0.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.services = {}  # Service name -> CircuitBreaker state

    def get_service_circuit(self, service_name: str) -> Dict[str, Any]:
        """
        Get or create circuit for a service.

        Args:
            service_name (str): Service name

        Returns:
            Dict[str, Any]: Service circuit
        """
        if service_name not in self.services:
            self.services[service_name] = {
                "state": CircuitState.CLOSED,
                "failure_count": 0,
                "last_failure_time": None,
            }

        return self.services[service_name]

    def record_success(self, service_name: str) -> None:
        """
        Record a successful request.

        Args:
            service_name (str): Service name
        """
        circuit = self.get_service_circuit(service_name)

        # Reset circuit if it was half-open
        if circuit["state"] == CircuitState.HALF_OPEN:
            circuit["state"] = CircuitState.CLOSED
            circuit["failure_count"] = 0
            circuit["last_failure_time"] = None

    def record_failure(self, service_name: str) -> None:
        """
        Record a failed request.

        Args:
            service_name (str): Service name
        """
        circuit = self.get_service_circuit(service_name)

        # Increment failure count
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = datetime.now(timezone.utc)

        # Open circuit if threshold is reached
        if (
            circuit["state"] == CircuitState.CLOSED
            and circuit["failure_count"] >= self.failure_threshold
        ):
            circuit["state"] = CircuitState.OPEN

    def is_circuit_open(self, service_name: str) -> bool:
        """
        Check if circuit is open for a service.

        Args:
            service_name (str): Service name

        Returns:
            bool: True if circuit is open, False otherwise
        """
        circuit = self.get_service_circuit(service_name)

        # Check if circuit is open
        if circuit["state"] == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if circuit["last_failure_time"] and datetime.now(timezone.utc) - circuit[
                "last_failure_time"
            ] > timedelta(seconds=self.recovery_timeout):
                # Set circuit to half-open to test if service is back online
                circuit["state"] = CircuitState.HALF_OPEN
                return False

            return True

        return False

    async def call_service(
        self, service_name: str, url: str, method: str, **kwargs
    ) -> httpx.Response:
        """
        Call a service with circuit breaker protection.

        Args:
            service_name (str): Service name
            url (str): Request URL
            method (str): HTTP method
            **kwargs: Additional arguments for httpx

        Returns:
            httpx.Response: Response

        Raises:
            HTTPException: If circuit is open or request fails
        """
        # Check if circuit is open
        if self.is_circuit_open(service_name):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {service_name} is unavailable",
            )

        try:
            # Make request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await getattr(client, method.lower())(url, **kwargs)

                # Record success
                self.record_success(service_name)

                return response
        except (httpx.RequestError, asyncio.TimeoutError) as e:
            # Record failure
            self.record_failure(service_name)

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {service_name} is unavailable: {str(e)}",
            )


# Create global circuit breaker
circuit_breaker = CircuitBreaker()


async def circuit_breaker_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[JSONResponse]]
) -> JSONResponse:
    """
    Middleware for circuit breaker.

    Args:
        request (Request): FastAPI request
        call_next (Callable): Next middleware or route handler

    Returns:
        JSONResponse: Response
    """
    # Extract service name from path
    path_parts = request.url.path.strip("/").split("/")
    service_name = path_parts[0] if path_parts else "unknown"

    # Check if circuit is open
    if circuit_breaker.is_circuit_open(service_name):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": f"Service {service_name} is unavailable"},
        )

    try:
        # Continue with request
        response = await call_next(request)

        # Record success
        circuit_breaker.record_success(service_name)

        return response
    except Exception as e:
        # Record failure
        circuit_breaker.record_failure(service_name)

        # Re-raise exception
        raise e
