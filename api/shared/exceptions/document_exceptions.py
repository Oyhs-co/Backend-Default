from typing import Any, Dict, Optional

from .base_exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)


class DocumentNotFoundException(NotFoundException):
    """Exception for document not found"""

    def __init__(
        self,
        detail: str = "Document not found",
        error_code: str = "DOCUMENT_NOT_FOUND",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class DocumentVersionNotFoundException(NotFoundException):
    """Exception for document version not found"""

    def __init__(
        self,
        detail: str = "Document version not found",
        error_code: str = "DOCUMENT_VERSION_NOT_FOUND",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class DocumentPermissionNotFoundException(NotFoundException):
    """Exception for document permission not found"""

    def __init__(
        self,
        detail: str = "Document permission not found",
        error_code: str = "DOCUMENT_PERMISSION_NOT_FOUND",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class InsufficientDocumentPermissionException(ForbiddenException):
    """Exception for insufficient document permission"""

    def __init__(
        self,
        detail: str = "Insufficient document permission",
        error_code: str = "INSUFFICIENT_DOCUMENT_PERMISSION",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class DocumentStorageException(BadRequestException):
    """Exception for document storage errors"""

    def __init__(
        self,
        detail: str = "Document storage error",
        error_code: str = "DOCUMENT_STORAGE_ERROR",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class DocumentSizeLimitExceededException(BadRequestException):
    """Exception for exceeding document size limit"""

    def __init__(
        self,
        detail: str = "Document size limit exceeded",
        error_code: str = "DOCUMENT_SIZE_LIMIT_EXCEEDED",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class InvalidDocumentTypeException(BadRequestException):
    """Exception for invalid document type"""

    def __init__(
        self,
        detail: str = "Invalid document type",
        error_code: str = "INVALID_DOCUMENT_TYPE",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)


class DocumentLimitExceededException(BadRequestException):
    """Exception for exceeding document limit"""

    def __init__(
        self,
        detail: str = "Document limit exceeded",
        error_code: str = "DOCUMENT_LIMIT_EXCEEDED",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail=detail, error_code=error_code, headers=headers)
