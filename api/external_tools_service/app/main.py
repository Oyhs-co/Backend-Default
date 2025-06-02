from typing import Any, List

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Path, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.external_tools_service.app.schemas.external_tools import (
    ExternalToolConnectionCreateDTO,
    ExternalToolConnectionDTO,
    OAuthCallbackDTO,
    OAuthProviderDTO,
    OAuthRequestDTO,
)
from api.external_tools_service.app.services.external_tools_service import (
    ExternalToolsService,
)
from api.shared.exceptions.auth_exceptions import InvalidTokenException
from api.shared.utils.db import get_db
from api.shared.utils.jwt import decode_token

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TaskHub External Tools Service",
    description="External tools integration service for TaskHub platform",
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

# Create OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Security(oauth2_scheme)) -> str:
    """
    Get current user ID from token.

    Args:
        token (str): JWT token

    Returns:
        str: User ID

    Raises:
        InvalidTokenException: If token is invalid
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenException()

        return user_id
    except Exception:
        raise InvalidTokenException()


# OAuth provider endpoints
@app.get(
    "/oauth/providers", response_model=List[OAuthProviderDTO], tags=["OAuth Providers"]
)
async def get_oauth_providers(
    db: Session = Depends(get_db), user_id: str = Depends(get_current_user)
):
    """
    Get OAuth providers.

    Args:
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[OAuthProviderDTO]: List of OAuth providers
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.get_oauth_providers()


@app.get(
    "/oauth/providers/{provider_id}",
    response_model=OAuthProviderDTO,
    tags=["OAuth Providers"],
)
async def get_oauth_provider(
    provider_id: str = Path(..., description="Provider ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get OAuth provider.

    Args:
        provider_id (str): Provider ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        OAuthProviderDTO: OAuth provider
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.get_oauth_provider(provider_id)


@app.post("/oauth/authorize", response_model=str, tags=["OAuth"])
async def get_oauth_url(
    request_data: OAuthRequestDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get OAuth authorization URL.

    Args:
        request_data (OAuthRequestDTO): Request data
        db (Session): Database session
        user_id (str): User ID

    Returns:
        str: Authorization URL
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.get_oauth_url(request_data)


@app.post("/oauth/callback", response_model=ExternalToolConnectionDTO, tags=["OAuth"])
async def handle_oauth_callback(
    callback_data: OAuthCallbackDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Handle OAuth callback.

    Args:
        callback_data (OAuthCallbackDTO): Callback data
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ExternalToolConnectionDTO: External tool connection
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.handle_oauth_callback(callback_data, user_id)


# External tool connection endpoints
@app.post(
    "/connections", response_model=ExternalToolConnectionDTO, tags=["Connections"]
)
async def create_connection(
    connection_data: ExternalToolConnectionCreateDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Create external tool connection.

    Args:
        connection_data (ExternalToolConnectionCreateDTO): Connection data
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ExternalToolConnectionDTO: Created connection
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.create_connection(connection_data, user_id)


@app.get(
    "/connections", response_model=List[ExternalToolConnectionDTO], tags=["Connections"]
)
async def get_user_connections(
    db: Session = Depends(get_db), user_id: str = Depends(get_current_user)
):
    """
    Get connections for current user.

    Args:
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[ExternalToolConnectionDTO]: List of connections
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.get_user_connections(user_id)


@app.get(
    "/connections/{connection_id}",
    response_model=ExternalToolConnectionDTO,
    tags=["Connections"],
)
async def get_connection(
    connection_id: str = Path(..., description="Connection ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get a connection.

    Args:
        connection_id (str): Connection ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ExternalToolConnectionDTO: Connection
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.get_connection(connection_id, user_id)


@app.post(
    "/connections/{connection_id}/refresh",
    response_model=ExternalToolConnectionDTO,
    tags=["Connections"],
)
async def refresh_connection(
    connection_id: str = Path(..., description="Connection ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Refresh connection token.

    Args:
        connection_id (str): Connection ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ExternalToolConnectionDTO: Updated connection
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.refresh_connection(connection_id, user_id)


@app.post("/connections/{connection_id}/revoke", tags=["Connections"])
async def revoke_connection(
    connection_id: str = Path(..., description="Connection ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Revoke connection.

    Args:
        connection_id (str): Connection ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Dict[str, Any]: Success response
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.revoke_connection(connection_id, user_id)


@app.delete("/connections/{connection_id}", tags=["Connections"])
async def delete_connection(
    connection_id: str = Path(..., description="Connection ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Delete connection.

    Args:
        connection_id (str): Connection ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Dict[str, Any]: Success response
    """
    external_tools_service = ExternalToolsService(db)
    return external_tools_service.delete_connection(connection_id, user_id)


@app.get("/health", tags=["Health"])
async def health_check() -> Any:
    """
    Health check endpoint.

    Returns:
        Dict[str, str]: Health status
    """
    return {"status": "healthy"}
