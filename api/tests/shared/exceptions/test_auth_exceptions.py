from api.shared.exceptions.auth_exceptions import (
    InvalidCredentialsException, TokenExpiredException, InvalidTokenException,
    EmailAlreadyExistsException, InsufficientPermissionsException,
    AccountNotVerifiedException, AccountDisabledException
)

def test_invalid_credentials() -> None:
    exc = InvalidCredentialsException()
    assert exc.status_code == 401
    assert exc.detail['message'] == 'Invalid email or password'  # type: ignore
    assert exc.detail['error_code'] == 'INVALID_CREDENTIALS'  # type: ignore

def test_token_expired() -> None:
    exc = TokenExpiredException()
    assert exc.status_code == 401
    assert exc.detail['message'] == 'Token has expired'  # type: ignore
    assert exc.detail['error_code'] == 'TOKEN_EXPIRED'  # type: ignore

def test_invalid_token() -> None:
    exc = InvalidTokenException()
    assert exc.status_code == 401
    assert exc.detail['message'] == 'Invalid token'  # type: ignore
    assert exc.detail['error_code'] == 'INVALID_TOKEN'  # type: ignore

def test_email_already_exists() -> None:
    exc = EmailAlreadyExistsException()
    assert exc.status_code == 409
    assert exc.detail['message'] == 'Email already exists'  # type: ignore
    assert exc.detail['error_code'] == 'EMAIL_ALREADY_EXISTS'  # type: ignore

def test_insufficient_permissions() -> None:
    exc = InsufficientPermissionsException()
    assert exc.status_code == 403
    assert exc.detail['message'] == 'Insufficient permissions'  # type: ignore
    assert exc.detail['error_code'] == 'INSUFFICIENT_PERMISSIONS'  # type: ignore

def test_account_not_verified() -> None:
    exc = AccountNotVerifiedException()
    assert exc.status_code == 403
    assert exc.detail['message'] == 'Account not verified'  # type: ignore
    assert exc.detail['error_code'] == 'ACCOUNT_NOT_VERIFIED'  # type: ignore

def test_account_disabled() -> None:
    exc = AccountDisabledException()
    assert exc.status_code == 403
    assert exc.detail['message'] == 'Account is disabled'  # type: ignore
    assert exc.detail['error_code'] == 'ACCOUNT_DISABLED'  # type: ignore 