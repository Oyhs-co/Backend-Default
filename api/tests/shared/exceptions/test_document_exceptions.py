import pytest
from api.shared.exceptions.document_exceptions import (
    DocumentNotFoundException, DocumentVersionNotFoundException, DocumentPermissionNotFoundException,
    InsufficientDocumentPermissionException, DocumentStorageException, DocumentSizeLimitExceededException,
    InvalidDocumentTypeException, DocumentLimitExceededException
)

def test_document_not_found() -> None:
    exc = DocumentNotFoundException()
    assert exc.status_code == 404
    assert exc.detail['message'] == 'Document not found'
    assert exc.detail['error_code'] == 'DOCUMENT_NOT_FOUND'

def test_document_version_not_found() -> None:
    exc = DocumentVersionNotFoundException()
    assert exc.status_code == 404
    assert exc.detail['message'] == 'Document version not found'
    assert exc.detail['error_code'] == 'DOCUMENT_VERSION_NOT_FOUND'

def test_document_permission_not_found() -> None:
    exc = DocumentPermissionNotFoundException()
    assert exc.status_code == 404
    assert exc.detail['message'] == 'Document permission not found'
    assert exc.detail['error_code'] == 'DOCUMENT_PERMISSION_NOT_FOUND'

def test_insufficient_document_permission() -> None:
    exc = InsufficientDocumentPermissionException()
    assert exc.status_code == 403
    assert exc.detail['message'] == 'Insufficient document permission'
    assert exc.detail['error_code'] == 'INSUFFICIENT_DOCUMENT_PERMISSION'

def test_document_storage_exception() -> None:
    exc = DocumentStorageException()
    assert exc.status_code == 400
    assert exc.detail['message'] == 'Document storage error'
    assert exc.detail['error_code'] == 'DOCUMENT_STORAGE_ERROR'

def test_document_size_limit_exceeded() -> None:
    exc = DocumentSizeLimitExceededException()
    assert exc.status_code == 400
    assert exc.detail['message'] == 'Document size limit exceeded'
    assert exc.detail['error_code'] == 'DOCUMENT_SIZE_LIMIT_EXCEEDED'

def test_invalid_document_type() -> None:
    exc = InvalidDocumentTypeException()
    assert exc.status_code == 400
    assert exc.detail['message'] == 'Invalid document type'
    assert exc.detail['error_code'] == 'INVALID_DOCUMENT_TYPE'

def test_document_limit_exceeded() -> None:
    exc = DocumentLimitExceededException()
    assert exc.status_code == 400
    assert exc.detail['message'] == 'Document limit exceeded'
    assert exc.detail['error_code'] == 'DOCUMENT_LIMIT_EXCEEDED' 