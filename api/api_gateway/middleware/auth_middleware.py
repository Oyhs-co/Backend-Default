import os
from typing import Awaitable, Callable, Optional

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Auth service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")


async def auth_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[JSONResponse]]
) -> JSONResponse:
    """
    Middleware for authentication.

    Args:
        request (Request): FastAPI request
        call_next (Callable[[Request], Awaitable[JSONResponse]]): Next middleware or route handler

    Returns:
        JSONResponse: Response
    """
    # Skip authentication for certain paths
    if _should_skip_auth(request.url.path):
        return await call_next(request)

    # Get token from request
    token = _get_token_from_request(request)

    # Check if token exists
    if not token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"},
        )

    # Validate token
    try:
        user_id = await _validate_token(token)

        # Add user ID to request state
        request.state.user_id = user_id

        # Continue with request
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)},
        )


def _should_skip_auth(path: str) -> bool:
    """
    Check if authentication should be skipped for a path.

    Args:
        path (str): Request path

    Returns:
        bool: True if authentication should be skipped, False otherwise
    """
    # Skip authentication for health check and auth endpoints
    skip_paths = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
    ]

    return any(path.startswith(skip_path) for skip_path in skip_paths)


def _get_token_from_request(request: Request) -> Optional[str]:
    """
    Get token from request.

    Args:
        request (Request): FastAPI request

    Returns:
        Optional[str]: Token or None
    """
    # Get token from Authorization header
    authorization = request.headers.get("Authorization")

    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")

    return None


async def _validate_token(token: str) -> str:
    """
    Validate token with auth service.

    Args:
        token (str): JWT token

    Returns:
        str: User ID

    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Make request to auth service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/validate",
                headers={"Authorization": f"Bearer {token}"},
            )

            # Check response
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            # Parse response
            data = response.json()

            # Extract user ID from token
            # In a real application, you would decode the token and extract the user ID
            # For simplicity, we'll assume the auth service returns the user ID
            user_id = data.get("user_id")

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token, user_id not in response",
                )

            return user_id
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service unavailable: {str(e)}",
        )
    except Exception as e:
        # It's good practice to log the error here
        # logger.error(f"Unexpected error during token validation with auth service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while validating the token.",
        )
