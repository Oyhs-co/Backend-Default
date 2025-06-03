from api.shared.models.external_tools import OAuthProvider, ExternalToolConnection, ExternalResource
from datetime import datetime

def test_oauth_provider_model_instantiation():
    provider = OAuthProvider(
        id='oid', name='GitHub', type='github', auth_url='https://auth', token_url='https://token', scope='repo',
        client_id='cid', client_secret='secret', redirect_uri='https://cb', created_at=datetime.now()
    )
    assert provider.name == 'GitHub'
    assert provider.type == 'github'
    assert provider.auth_url == 'https://auth'
    assert provider.token_url == 'https://token'
    assert provider.client_id == 'cid'
    assert provider.redirect_uri == 'https://cb'

def test_external_tool_connection_model_instantiation():
    conn = ExternalToolConnection(
        id='cid', user_id='uid', provider_id='oid', access_token='tok', is_active=True, created_at=datetime.now()
    )
    assert conn.user_id == 'uid'
    assert conn.provider_id == 'oid'
    assert conn.access_token == 'tok'
    assert conn.is_active is True

def test_external_resource_model_instantiation():
    res = ExternalResource(
        id='rid', connection_id='cid', resource_id='extid', name='file', type='file', created_at=datetime.now()
    )
    assert res.connection_id == 'cid'
    assert res.resource_id == 'extid'
    assert res.name == 'file'
    assert res.type == 'file' 