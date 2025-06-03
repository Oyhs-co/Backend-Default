import pytest
from api.external_tools_service.app.adapters.oauth_adapter import (
    OAuthAdapterFactory, GitHubOAuthAdapter, GoogleOAuthAdapter
)
from api.external_tools_service.app.schemas.external_tools import ExternalToolType
from api.shared.models.external_tools import OAuthProvider
from unittest.mock import MagicMock, patch

@pytest.fixture
def github_provider() -> OAuthProvider:
    provider = MagicMock()
    provider.client_id = 'cid'
    provider.client_secret = 'secret'
    provider.auth_url = 'https://github.com/login/oauth/authorize'
    provider.token_url = 'https://github.com/login/oauth/access_token'
    provider.scope = 'repo'
    provider.redirect_uri = 'https://app/callback'
    provider.additional_params = None
    return provider

@pytest.fixture
def google_provider() -> OAuthProvider:
    provider = MagicMock()
    provider.client_id = 'cid'
    provider.client_secret = 'secret'
    provider.auth_url = 'https://accounts.google.com/o/oauth2/auth'
    provider.token_url = 'https://oauth2.googleapis.com/token'
    provider.scope = 'drive'
    provider.redirect_uri = 'https://app/callback'
    provider.additional_params = None
    return provider

def test_factory_github():
    factory = OAuthAdapterFactory()
    adapter = factory.create_adapter(ExternalToolType.GITHUB)
    assert isinstance(adapter, GitHubOAuthAdapter)

def test_factory_google():
    factory = OAuthAdapterFactory()
    adapter = factory.create_adapter(ExternalToolType.GOOGLE_DRIVE)
    assert isinstance(adapter, GoogleOAuthAdapter)

def test_factory_invalid():
    factory = OAuthAdapterFactory()
    with pytest.raises(ValueError):
        factory.create_adapter('invalid')  # type: ignore

def test_github_auth_url(github_provider: OAuthProvider):
    adapter = GitHubOAuthAdapter()
    url = adapter.get_auth_url(github_provider, state='abc')
    assert 'client_id=cid' in url
    assert 'state=abc' in url
    assert str(github_provider.auth_url) in url

def test_github_exchange_code_for_token_error(github_provider: OAuthProvider):
    adapter = GitHubOAuthAdapter()
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = 'fail'
        with pytest.raises(Exception):
            adapter.exchange_code_for_token(github_provider, 'code')

def test_github_get_user_info_error(github_provider: OAuthProvider):
    adapter = GitHubOAuthAdapter()
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 400
        mock_get.return_value.text = 'fail'
        with pytest.raises(Exception):
            adapter.get_user_info(github_provider, 'token')

def test_github_refresh_token_not_implemented(github_provider: OAuthProvider):
    adapter = GitHubOAuthAdapter()
    with pytest.raises(NotImplementedError):
        adapter.refresh_token(github_provider, 'refresh')

def test_google_auth_url(google_provider: OAuthProvider):
    adapter = GoogleOAuthAdapter()
    url = adapter.get_auth_url(google_provider, state='xyz')
    assert 'client_id=cid' in url
    assert 'state=xyz' in url
    assert str(google_provider.auth_url) in url

def test_google_exchange_code_for_token_error(google_provider: OAuthProvider):
    adapter = GoogleOAuthAdapter()
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = 'fail'
        with pytest.raises(Exception):
            adapter.exchange_code_for_token(google_provider, 'code')

def test_google_get_user_info_error(google_provider: OAuthProvider):
    adapter = GoogleOAuthAdapter()
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 400
        mock_get.return_value.text = 'fail'
        with pytest.raises(Exception):
            adapter.get_user_info(google_provider, 'token') 