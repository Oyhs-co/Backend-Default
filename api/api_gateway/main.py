from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.api_gateway.middleware.auth_middleware import auth_middleware
from api.api_gateway.middleware.circuit_breaker import (
    circuit_breaker,
    circuit_breaker_middleware,
)
from api.api_gateway.utils.service_registry import service_registry

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TaskHub API Gateway",
    description="API Gateway for TaskHub platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middlewares
app.middleware("http")(auth_middleware)
app.middleware("http")(circuit_breaker_middleware)


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
)
async def gateway(request: Request, path: str) -> Any:
    """
    Gateway for all requests.

    Args:
        request (Request): FastAPI request
        path (str): Request path

    Returns:
        Response: Response from service
    """
    # Get full path
    full_path = f"/{path}"

    try:
        # Get service for path
        service = service_registry.get_service_for_path(full_path, request.method)

        # Build target URL
        target_url = f"{service['url']}{full_path}"

        # Forward request to service
        return await forward_request(request, target_url, service["name"])
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(e)}
        )
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)},
        )


async def forward_request(
    request: Request, target_url: str, service_name: str
) -> JSONResponse:
    """
    Forward request to service.

    Args:
        request (Request): FastAPI request
        target_url (str): Target URL
        service_name (str): Service name

    Returns:
        JSONResponse: Response from service
    """
    # Get request body
    body = await request.body()

    # Get request headers
    headers = dict(request.headers)

    # Add user ID to headers if available
    if hasattr(request.state, "user_id"):
        headers["X-User-ID"] = request.state.user_id

    # Forward request to service using circuit breaker
    response = await circuit_breaker.call_service(  # type: ignore
        service_name=service_name,
        url=target_url,
        method=request.method,
        headers=headers,
        content=body,
        params=dict(request.query_params),
    )

    # Return response
    return JSONResponse(
        status_code=response.status_code,
        content=response.json() if response.content else None,
        headers=dict(response.headers),
    )


@app.get("/health", tags=["Health"])
async def health_check() -> Any:
    """
    Health check endpoint.

    Returns:
        Dict[str, Any]: Health status
    """
    return {"status": "healthy"}


@app.get("/services", tags=["Services"])
async def get_services() -> Any:
    """
    Get all services.

    Returns:

        List[Dict[str, Any]]: List of services

    """
    return service_registry.get_all_services()

# Export para tests de integración
# (No existen get_db ni get_current_user aquí, pero exporto auth_middleware por consistencia)
auth_middleware = auth_middleware
