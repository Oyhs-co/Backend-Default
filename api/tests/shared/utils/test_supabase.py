from unittest.mock import patch, MagicMock
from api.shared.utils.supabase import SupabaseManager

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