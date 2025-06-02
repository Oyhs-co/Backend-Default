from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api.auth_service.app.schemas.user import (
    TokenDTO,
    TokenValidationResponseDTO,
    UserProfileDTO,
    UserRegisterDTO,
)
from api.auth_service.app.services.auth_service import AuthService

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TaskHub Auth Service",
    description="Authentication service for TaskHub platform",
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

# Create AuthService instance
auth_service = AuthService()


@app.post("/auth/register", response_model=TokenDTO, tags=["Authentication"])
async def register(user_data: UserRegisterDTO) -> Any:
    """
    Register a new user.

    Args:
        user_data (UserRegisterDTO): User registration data

    Returns:
        TokenDTO: Authentication tokens
    """
    return auth_service.register(user_data)


@app.post("/auth/login", response_model=TokenDTO, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login a user.

    Args:
        form_data (OAuth2PasswordRequestForm): Login form data

    Returns:
        TokenDTO: Authentication tokens
    """
    return auth_service.login(form_data.username, form_data.password)


@app.get(
    "/auth/validate", response_model=TokenValidationResponseDTO, tags=["Authentication"]
)
async def validate(token: str = Security(oauth2_scheme)):
    """
    Validate a token. Also returns user_id along with new tokens.

    Args:
        token (str): JWT token
    """
    return auth_service.validate_token(token)


@app.post("/auth/refresh", response_model=TokenDTO, tags=["Authentication"])
async def refresh(refresh_token: str) -> Any:
    """
    Refresh a token.

    Args:
        refresh_token (str): Refresh token

    Returns:
        TokenDTO: Authentication tokens
    """
    return auth_service.refresh_token(refresh_token)


@app.post("/auth/logout", tags=["Authentication"])
async def logout(token: str = Security(oauth2_scheme)):
    """
    Logout a user.

    Args:
        token (str): JWT token

    Returns:
        Dict[str, Any]: Logout response
    """
    return auth_service.logout(token)


@app.get("/auth/profile", response_model=UserProfileDTO, tags=["User"])
async def get_profile(token: str = Security(oauth2_scheme)):
    """
    Get user profile.

    Args:
        token (str): JWT token

    Returns:
        UserProfileDTO: User profile
    """
    return auth_service.get_user_profile(token)


@app.get("/health", tags=["Health"])
async def health_check() -> Any:
    """
    Health check endpoint.

    Returns:
        Dict[str, str]: Health status
    """
    return {"status": "healthy"}
