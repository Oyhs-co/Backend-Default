import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from api.auth_service.app.schemas.user import TokenDTO, UserProfileDTO, UserRegisterDTO
from api.shared.exceptions.auth_exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
)
from api.shared.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    is_token_valid,
)
from api.shared.utils.supabase import SupabaseManager


class AuthService:
    """Service for authentication operations"""

    def __init__(self):
        """Initialize AuthService with SupabaseManager"""
        self.supabase_manager = SupabaseManager()
        self.token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    def register(self, user_data: UserRegisterDTO) -> TokenDTO:
        """
        Register a new user.

        Args:
            user_data (UserRegisterDTO): User registration data

        Returns:
            TokenDTO: Authentication tokens

        Raises:
            EmailAlreadyExistsException: If email already exists
        """
        try:
            # Create user metadata
            user_metadata = {
                "full_name": user_data.full_name,
                "company_name": user_data.company_name,
            }

            # Sign up user in Supabase
            response = self.supabase_manager.sign_up(
                user_data.email, user_data.password, user_metadata
            )

            # Get user data
            user = response.user

            # Create tokens
            access_token = create_access_token({"sub": user.id})
            refresh_token = create_refresh_token({"sub": user.id})

            # Calculate expiration time
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=self.token_expire_minutes
            )

            # Return tokens
            return TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
        except Exception as _e:
            # Check if email already exists
            if "already exists" in str(_e):
                raise EmailAlreadyExistsException()
            raise _e

    def login(self, email: str, password: str) -> TokenDTO:
        """
        Login a user.

        Args:
            email (str): User email
            password (str): User password

        Returns:
            TokenDTO: Authentication tokens

        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        try:
            # Sign in user in Supabase
            response = self.supabase_manager.sign_in(email, password)

            # Get user data
            user = response.user

            # Create tokens
            access_token = create_access_token({"sub": user.id})
            refresh_token = create_refresh_token({"sub": user.id})

            # Calculate expiration time
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=self.token_expire_minutes
            )

            # Return tokens
            return TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
        except Exception as _e:
            # Invalid credentials
            raise InvalidCredentialsException()

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a token.

        Args:
            token (str): JWT token

        Returns:
            Dict[str, Any]: User ID and Authentication tokens

        Raises:
            InvalidTokenException: If token is invalid
            TokenExpiredException: If token has expired
        """
        # decode_token from shared.utils.jwt already raises TokenExpiredException or InvalidTokenException
        payload = decode_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenException("User ID (sub) not found in token payload")

        # Create new tokens
        access_token = create_access_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})

        # Calculate expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.token_expire_minutes
        )

        # Return user_id and tokens
        return {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_at": expires_at,
        }

    def refresh_token(self, refresh_token: str) -> TokenDTO:
        """
        Refresh a token.

        Args:
            refresh_token (str): Refresh token

        Returns:
            TokenDTO: Authentication tokens

        Raises:
            InvalidTokenException: If token is invalid
            TokenExpiredException: If token has expired
        """
        try:
            # Decode token
            payload = decode_token(refresh_token)

            # Check if token is valid
            if not is_token_valid(refresh_token):
                raise InvalidTokenException()

            # Get user ID
            user_id = payload.get("sub")

            # Create new tokens
            access_token = create_access_token({"sub": user_id})
            new_refresh_token = create_refresh_token({"sub": user_id})

            # Calculate expiration time
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=self.token_expire_minutes
            )

            # Return tokens
            return TokenDTO(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_at=expires_at,
            )
        except Exception as _e:
            # Check if token has expired
            if "expired" in str(_e):
                raise TokenExpiredException()

            # Invalid token
            raise InvalidTokenException()

    def logout(self, token: str) -> Dict[str, Any]:
        """
        Logout a user.

        Args:
            token (str): JWT token

        Returns:
            Dict[str, Any]: Logout response

        Raises:
            InvalidTokenException: If token is invalid
        """
        try:
            # Sign out user in Supabase
            self.supabase_manager.sign_out(token)

            # Return success response
            return {"message": "Logged out successfully"}
        except Exception as _e:
            # Invalid token
            raise InvalidTokenException()

    def get_user_profile(self, token: str) -> UserProfileDTO:
        """
        Get user profile.

        Args:
            token (str): JWT token

        Returns:
            UserProfileDTO: User profile

        Raises:
            InvalidTokenException: If token is invalid
        """
        try:
            # Get user from Supabase
            response = self.supabase_manager.get_user(token)

            # Get user data
            user = response.user

            # Safely access user metadata
            user_metadata = getattr(user, "user_metadata", {}) or {}
            if not isinstance(user_metadata, dict):
                user_metadata = {}

            # Return user profile
            return UserProfileDTO(
                id=user.id,
                email=user.email,
                full_name=user_metadata.get("full_name", ""),
                company_name=user_metadata.get("company_name", ""),
                role="user",  # Default role
                created_at=datetime.fromisoformat(user.created_at),
                updated_at=(
                    datetime.fromisoformat(user.updated_at) if user.updated_at else None
                ),
            )
        except Exception as _e:
            # Invalid token
            raise InvalidTokenException()
