from typing import Any, Dict, Optional

from .base_exceptions import (
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
)


class InvalidCredentialsException(UnauthorizedException):
    """Exception for invalid credentials"""

    def __init__(
        self,
        detail: str = "Invalid email or password",
        error_code: str = "INVALID_CREDENTIALS",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class TokenExpiredException(UnauthorizedException):
    """Exception for expired tokens"""

    def __init__(
        self,
        detail: str = "Token has expired",
        error_code: str = "TOKEN_EXPIRED",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class InvalidTokenException(UnauthorizedException):
    """Exception for invalid tokens"""

    def __init__(
        self,
        detail: str = "Invalid token",
        error_code: str = "INVALID_TOKEN",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class EmailAlreadyExistsException(ConflictException):
    """Exception for email already exists"""

    def __init__(
        self,
        detail: str = "Email already exists",
        error_code: str = "EMAIL_ALREADY_EXISTS",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class InsufficientPermissionsException(ForbiddenException):
    """Exception for insufficient permissions"""

    def __init__(
        self,
        detail: str = "Insufficient permissions",
        error_code: str = "INSUFFICIENT_PERMISSIONS",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class AccountNotVerifiedException(ForbiddenException):
    """Exception for unverified accounts"""

    def __init__(
        self,
        detail: str = "Account not verified",
        error_code: str = "ACCOUNT_NOT_VERIFIED",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class AccountDisabledException(ForbiddenException):
    """Exception for disabled accounts"""

    def __init__(
        self,
        detail: str = "Account is disabled",
        error_code: str = "ACCOUNT_DISABLED",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)
