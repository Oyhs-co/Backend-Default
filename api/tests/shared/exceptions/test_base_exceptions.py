import pytest
from api.shared.exceptions.base_exceptions import (
    BaseAPIException, NotFoundException, UnauthorizedException, ForbiddenException,
    BadRequestException, ConflictException, InternalServerException, ServiceUnavailableException, ValidationException
)

def test_base_api_exception() -> None:
    exc = BaseAPIException(418, 'I am a teapot', 'TEAPOT')
    assert exc.status_code == 418
    assert exc.detail['message'] == 'I am a teapot'
    assert exc.detail['error_code'] == 'TEAPOT'

def test_not_found_exception() -> None:
    exc = NotFoundException()
    assert exc.status_code == 404
    assert exc.detail['message'] == 'Resource not found'
    assert exc.detail['error_code'] == 'NOT_FOUND'

def test_unauthorized_exception() -> None:
    exc = UnauthorizedException()
    assert exc.status_code == 401
    assert exc.detail['message'] == 'Unauthorized access'
    assert exc.detail['error_code'] == 'UNAUTHORIZED'

def test_forbidden_exception() -> None:
    exc = ForbiddenException()
    assert exc.status_code == 403
    assert exc.detail['message'] == 'Forbidden access'
    assert exc.detail['error_code'] == 'FORBIDDEN'

def test_bad_request_exception() -> None:
    exc = BadRequestException()
    assert exc.status_code == 400
    assert exc.detail['message'] == 'Bad request'
    assert exc.detail['error_code'] == 'BAD_REQUEST'

def test_conflict_exception() -> None:
    exc = ConflictException()
    assert exc.status_code == 409
    assert exc.detail['message'] == 'Conflict'
    assert exc.detail['error_code'] == 'CONFLICT'

def test_internal_server_exception() -> None:
    exc = InternalServerException()
    assert exc.status_code == 500
    assert exc.detail['message'] == 'Internal server error'
    assert exc.detail['error_code'] == 'INTERNAL_SERVER_ERROR'

def test_service_unavailable_exception() -> None:
    exc = ServiceUnavailableException()
    assert exc.status_code == 503
    assert exc.detail['message'] == 'Service unavailable'
    assert exc.detail['error_code'] == 'SERVICE_UNAVAILABLE'

def test_validation_exception() -> None:
    exc = ValidationException(errors={'field': 'error'})
    assert exc.status_code == 422
    # For ValidationException, message is a dict
    assert exc.detail['message']['message'] == 'Validation error'
    assert exc.detail['message']['error_code'] == 'VALIDATION_ERROR'
    assert exc.detail['message']['errors'] == {'field': 'error'}
    assert exc.detail['error_code'] == 'VALIDATION_ERROR' 