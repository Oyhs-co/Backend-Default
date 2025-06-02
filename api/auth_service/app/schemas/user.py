from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterDTO(BaseModel):
    """DTO for user registration"""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    company_name: Optional[str] = None


class UserLoginDTO(BaseModel):
    """DTO for user login"""

    email: EmailStr
    password: str


class TokenDTO(BaseModel):
    """DTO for authentication tokens"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


class TokenValidationResponseDTO(TokenDTO):
    """DTO for token validation response, including user_id"""

    user_id: str


class UserProfileDTO(BaseModel):
    """DTO for user profile information"""

    id: str
    email: EmailStr
    full_name: str
    company_name: Optional[str] = None
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class RolePermissionDTO(BaseModel):
    """DTO for role permissions"""

    role: str
    permissions: List[str]
