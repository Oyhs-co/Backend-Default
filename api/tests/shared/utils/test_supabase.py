from unittest.mock import patch, MagicMock
from api.shared.utils.supabase import SupabaseManager
import pytest

def test_singleton_instance():
    inst1 = SupabaseManager()
    inst2 = SupabaseManager()
    assert inst1 is inst2

def test_get_client():
    manager = SupabaseManager()
    with patch.object(manager, 'client', create=True) as mock_client:
        assert manager.get_client() == mock_client

def test_sign_up_calls_client():
    manager = SupabaseManager()
    with patch.object(manager, 'client', create=True) as mock_client:
        mock_client.auth.sign_up.return_value = MagicMock(user=MagicMock(id='uid'))
        result = manager.sign_up('a@b.com', 'pass', {'meta': 1})
        assert hasattr(result, 'user')

def test_sign_in_calls_client():
    manager = SupabaseManager()
    with patch.object(manager, 'client', create=True) as mock_client:
        mock_client.auth.sign_in_with_password.return_value = MagicMock(user=MagicMock(id='uid'))
        result = manager.sign_in('a@b.com', 'pass')
        assert hasattr(result, 'user')

def test_sign_in_without_client(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = SupabaseManager()
    monkeypatch.setattr(manager, 'client', None)
    with pytest.raises(Exception):
        manager.sign_in('a@b.com', 'pass')

def test_sign_up_error(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = SupabaseManager()
    class MockClient:
        class auth:
            @staticmethod
            def sign_up(*args: object, **kwargs: object) -> None:
                raise Exception("fail")
    monkeypatch.setattr(manager, 'client', MockClient())
    with pytest.raises(Exception):
        manager.sign_up('a@b.com', 'pass', {}) 