from datetime import timedelta, datetime, timezone
from typing import Any, Dict
import pytest
from jose import JWTError
from unittest.mock import patch
from api.shared.utils import jwt as jwt_utils

@pytest.fixture(autouse=True)
def setup_jwt_env(monkeypatch: Any):
    # Mock JWT module attributes directly instead of using env vars
    monkeypatch.setattr(jwt_utils, 'JWT_SECRET_KEY', 'testsecret')
    monkeypatch.setattr(jwt_utils, 'JWT_ALGORITHM', 'HS256')
    monkeypatch.setattr(jwt_utils, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
    monkeypatch.setattr(jwt_utils, 'REFRESH_TOKEN_EXPIRE_DAYS', 7)
    yield

def test_create_and_decode_access_token():
    data = {'sub': 'user123'}
    token = jwt_utils.create_access_token(data)
    decoded = jwt_utils.decode_token(token)
    assert decoded['sub'] == 'user123'
    assert 'exp' in decoded

def test_create_and_decode_refresh_token():
    data = {'sub': 'user123'}
    token = jwt_utils.create_refresh_token(data)
    decoded = jwt_utils.decode_token(token)
    assert decoded['sub'] == 'user123'
    assert 'exp' in decoded
    # Verify refresh token expiration is longer than access token
    exp = datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc) + timedelta(days=6)

def test_is_token_valid():
    data = {'sub': 'user123'}
    token = jwt_utils.create_access_token(data)
    assert jwt_utils.is_token_valid(token)
    exp = jwt_utils.get_token_expiration(token)
    assert exp and exp > datetime.now(timezone.utc)

def test_token_expiration():
    now = datetime.now(timezone.utc)
    with patch('api.shared.utils.jwt.datetime') as mock_datetime, \
         patch('jose.jwt.decode') as mock_decode:
        mock_datetime.now.return_value = now
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        data = {'sub': 'user123'}
        token = jwt_utils.create_access_token(data, expires_delta=timedelta(seconds=1))
        # Simulate time passing
        mock_datetime.now.return_value = now + timedelta(seconds=2)
        mock_decode.side_effect = jwt_utils.JWTError('Token has expired')
        assert not jwt_utils.is_token_valid(token)

def test_invalid_token():
    invalid_token = "invalid.token.value"
    assert not jwt_utils.is_token_valid(invalid_token)
    with pytest.raises(jwt_utils.JWTError):
        jwt_utils.decode_token(invalid_token)

def test_wrong_secret(monkeypatch: Any):
    data = {'sub': 'user123'}
    token = jwt_utils.create_access_token(data)
    
    # Change secret after token creation
    monkeypatch.setattr(jwt_utils, 'JWT_SECRET_KEY', 'othersecret')
    assert not jwt_utils.is_token_valid(token)
    with pytest.raises(jwt_utils.JWTError):
        jwt_utils.decode_token(token)
    # Restore original secret
    monkeypatch.setattr(jwt_utils, 'JWT_SECRET_KEY', 'testsecret')

def test_missing_claim():
    data = {}
    token = jwt_utils.create_access_token(data)
    decoded = jwt_utils.decode_token(token)
    assert 'sub' not in decoded
    assert 'exp' in decoded # Should always have expiration

def test_decode_token_invalid() -> None:
    with pytest.raises(jwt_utils.JWTError):
        jwt_utils.decode_token('invalid.token.here')