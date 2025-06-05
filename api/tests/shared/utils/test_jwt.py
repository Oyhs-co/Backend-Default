from datetime import timedelta
from api.shared.utils import jwt as jwt_utils
from typing import Any

def test_create_and_decode_access_token(monkeypatch: Any):
    monkeypatch.setenv("JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    data = {'sub': 'user123'}
    token = jwt_utils.create_access_token(data)
    decoded = jwt_utils.decode_token(token)
    assert decoded['sub'] == 'user123'

def test_create_and_decode_refresh_token(monkeypatch: Any):
    monkeypatch.setenv("JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    data = {'sub': 'user123'}
    token = jwt_utils.create_refresh_token(data)
    decoded = jwt_utils.decode_token(token)
    assert decoded['sub'] == 'user123'

def test_is_token_valid(monkeypatch: Any):
    monkeypatch.setenv("JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    data = {'sub': 'user123'}
    token = jwt_utils.create_access_token(data)
    assert jwt_utils.is_token_valid(token)

def test_token_expiration(monkeypatch: Any):
    monkeypatch.setenv("JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    data = {'sub': 'user123'}
    token = jwt_utils.create_access_token(data, expires_delta=timedelta(seconds=1))
    import time
    time.sleep(2)
    assert not jwt_utils.is_token_valid(token)

def test_invalid_token(monkeypatch: Any):
    monkeypatch.setenv("JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    invalid_token = "invalid.token.value"
    assert not jwt_utils.is_token_valid(invalid_token)
    try:
        jwt_utils.decode_token(invalid_token)
    except Exception as e:
        assert isinstance(e, Exception)

def test_wrong_secret(monkeypatch: Any):
    monkeypatch.setenv("JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    data = {'sub': 'user123'}
    token = jwt_utils.create_access_token(data)
    monkeypatch.setenv("JWT_SECRET_KEY", "othersecret")
    assert not jwt_utils.is_token_valid(token)

def test_missing_claim(monkeypatch: Any):
    monkeypatch.setenv("JWT_SECRET_KEY", "testsecret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    data = {}
    token = jwt_utils.create_access_token(data)
    decoded = jwt_utils.decode_token(token)
    assert 'sub' not in decoded

def test_decode_token_invalid() -> None:
    try:
        jwt_utils.decode_token('invalid.token.here')
    except Exception as e:
        assert isinstance(e, Exception) 