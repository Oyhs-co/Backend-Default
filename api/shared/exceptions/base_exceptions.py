from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for API errors"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = "UNKNOWN_ERROR",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={"message": detail, "error_code": error_code},
            headers=headers,
        )


class NotFoundException(BaseAPIException):
    """Exception for resource not found errors"""

    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
            headers=headers,
        )


class UnauthorizedException(BaseAPIException):
    """Exception for unauthorized access errors"""

    def __init__(
        self,
        detail: str = "Unauthorized access",
        error_code: str = "UNAUTHORIZED",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers=headers,
        )


class ForbiddenException(BaseAPIException):
    """Exception for forbidden access errors"""

    def __init__(
        self,
        detail: str = "Forbidden access",
        error_code: str = "FORBIDDEN",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
            headers=headers,
        )


class BadRequestException(BaseAPIException):
    """Exception for bad request errors"""

    def __init__(
        self,
        detail: str = "Bad request",
        error_code: str = "BAD_REQUEST",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
            headers=headers,
        )


class ConflictException(BaseAPIException):
    """Exception for conflict errors"""

    def __init__(
        self,
        detail: str = "Conflict",
        error_code: str = "CONFLICT",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
            headers=headers,
        )


class InternalServerException(BaseAPIException):
    """Exception for internal server errors"""

    def __init__(
        self,
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_SERVER_ERROR",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
            headers=headers,
        )


class ServiceUnavailableException(BaseAPIException):
    """Exception for service unavailable errors"""

    def __init__(
        self,
        detail: str = "Service unavailable",
        error_code: str = "SERVICE_UNAVAILABLE",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code,
            headers=headers,
        )


class ValidationException(BaseAPIException):
    """Exception for validation errors"""

    def __init__(
        self,
        detail: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        errors: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        detail_dict = {"message": detail, "error_code": error_code}
        if errors:
            detail_dict["errors"] = errors

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail_dict,
            error_code=error_code,
            headers=headers,
        )
