import pytest
from unittest.mock import patch, MagicMock
from api.auth_service.app.services.auth_service import AuthService
from api.auth_service.app.schemas.user import UserRegisterDTO, UserProfileDTO
from api.shared.exceptions.auth_exceptions import InvalidCredentialsException, InvalidTokenException
from datetime import datetime, timezone
from typing import Generator

# Este fixture se aplica automáticamente a todos los tests del archivo
@pytest.fixture(autouse=True)
def patch_jwt_functions() -> Generator[None, None, None]:
    with patch("api.auth_service.app.services.auth_service.create_access_token", return_value="access_token"), \
         patch("api.auth_service.app.services.auth_service.create_refresh_token", return_value="refresh_token"), \
         patch("api.auth_service.app.services.auth_service.decode_token", return_value={"sub": "user123"}):
        yield

@pytest.fixture
def auth_service() -> AuthService:
    service = AuthService()
    service.supabase_manager = MagicMock()
    return service

def test_register_success(auth_service: AuthService) -> None:
    user_data = UserRegisterDTO(email="test@example.com", password="Test1234", full_name="Test User")
    mock_user = MagicMock(id="user123")
    with patch.object(auth_service.supabase_manager, "sign_up", return_value=MagicMock(user=mock_user)):
        result = auth_service.register(user_data)
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"

def test_login_success(auth_service: AuthService) -> None:
    mock_user = MagicMock()
    mock_user.id = 'user123'
    with patch.object(auth_service.supabase_manager, 'sign_in', return_value=MagicMock(user=mock_user)):
        with patch('api.auth_service.app.services.auth_service.create_access_token', return_value='access'):
            with patch('api.auth_service.app.services.auth_service.create_refresh_token', return_value='refresh'):
                result = auth_service.login('test@example.com', 'password')
                assert result.access_token == 'access'
                assert result.refresh_token == 'refresh'
                assert result.token_type == 'bearer'
                assert result.expires_at.tzinfo == timezone.utc

def test_login_invalid(auth_service: AuthService) -> None:
    with patch.object(auth_service.supabase_manager, 'sign_in', side_effect=Exception('fail')):
        with pytest.raises(InvalidCredentialsException):
            auth_service.login('bad@example.com', 'wrong')

def test_validate_token_success(auth_service: AuthService) -> None:
    with patch('api.auth_service.app.services.auth_service.decode_token', return_value={'sub': 'user123'}):
        with patch('api.auth_service.app.services.auth_service.create_access_token', return_value='access'):
            with patch('api.auth_service.app.services.auth_service.create_refresh_token', return_value='refresh'):
                result = auth_service.validate_token('sometoken')
                assert result['user_id'] == 'user123'
                assert result['access_token'] == 'access'
                assert result['refresh_token'] == 'refresh'
                assert result['token_type'] == 'bearer'
                assert result['expires_at'].tzinfo == timezone.utc

def test_validate_token_invalid(auth_service: AuthService) -> None:
    with patch('api.auth_service.app.services.auth_service.decode_token', return_value={}):
        with pytest.raises(InvalidTokenException):
            auth_service.validate_token('badtoken')

def test_get_user_profile_success(auth_service: AuthService) -> None:
    mock_user = MagicMock()
    mock_user.id = 'user123'
    mock_user.email = 'test@example.com'
    mock_user.user_metadata = {'full_name': 'Test User', 'company_name': 'TestCo'}
    mock_user.created_at = datetime.now(timezone.utc).isoformat()
    mock_user.updated_at = datetime.now(timezone.utc).isoformat()
    with patch.object(auth_service.supabase_manager, 'get_user', return_value=MagicMock(user=mock_user)):
        result = auth_service.get_user_profile('token')
        assert isinstance(result, UserProfileDTO)
        assert result.id == 'user123'
        assert result.email == 'test@example.com'
        assert result.full_name == 'Test User'
        assert result.company_name == 'TestCo'

def test_get_user_profile_invalid(auth_service: AuthService) -> None:
    with patch.object(auth_service.supabase_manager, 'get_user', side_effect=Exception('fail')):
        with pytest.raises(InvalidTokenException):
            auth_service.get_user_profile('badtoken') 