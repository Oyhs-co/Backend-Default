import pytest
from datetime import timedelta
from api.shared.utils import jwt

def test_create_and_decode_access_token() -> None:
    data = {'sub': 'user123'}
    token = jwt.create_access_token(data)
    decoded = jwt.decode_token(token)
    assert decoded['sub'] == 'user123'

def test_create_and_decode_refresh_token() -> None:
    data = {'sub': 'user123'}
    token = jwt.create_refresh_token(data)
    decoded = jwt.decode_token(token)
    assert decoded['sub'] == 'user123'

def test_is_token_valid() -> None:
    data = {'sub': 'user123'}
    token = jwt.create_access_token(data)
    assert jwt.is_token_valid(token)

def test_token_expiration() -> None:
    data = {'sub': 'user123'}
    expires = timedelta(seconds=1)
    token = jwt.create_access_token(data, expires_delta=expires)
    assert jwt.is_token_valid(token)
    import time
    time.sleep(2)
    assert not jwt.is_token_valid(token)

def test_decode_token_invalid() -> None:
    with pytest.raises(Exception):
        jwt.decode_token('invalid.token.here') 