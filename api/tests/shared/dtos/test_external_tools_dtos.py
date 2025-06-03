from datetime import datetime
from pydantic import HttpUrl, TypeAdapter
from api.shared.dtos.external_tools_dtos import (
    ExternalToolType, OAuthProviderDTO, OAuthRequestDTO, OAuthCallbackDTO,
    ExternalToolConnectionDTO, ExternalToolConnectionCreateDTO, ExternalResourceDTO, ExternalResourceSyncDTO
)

def test_external_tool_type_enum() -> None:
    assert ExternalToolType.GITHUB.value == 'github'
    assert ExternalToolType.TRELLO.value == 'trello'

def test_oauth_provider_dto() -> None:
    now = TypeAdapter(HttpUrl).validate_python('https://cb/')
    dto = OAuthProviderDTO(
        id='pid', name='GitHub', type=ExternalToolType.GITHUB,
        auth_url=TypeAdapter(HttpUrl).validate_python('https://auth/'),
        token_url=TypeAdapter(HttpUrl).validate_python('https://token/'),
        scope='repo', client_id='cid', redirect_uri=now
    )
    assert dto.id == 'pid'
    assert dto.type == ExternalToolType.GITHUB
    assert str(dto.auth_url) == 'https://auth/'
    assert str(dto.redirect_uri) == 'https://cb/'

def test_oauth_request_dto() -> None:
    dto = OAuthRequestDTO(provider_id='pid', redirect_uri=TypeAdapter(HttpUrl).validate_python('https://cb/'))
    assert dto.provider_id == 'pid'
    assert str(dto.redirect_uri) == 'https://cb/'

def test_oauth_callback_dto() -> None:
    dto = OAuthCallbackDTO(provider_id='pid', code='code', state='s', error=None)
    assert dto.provider_id == 'pid'
    assert dto.code == 'code'
    assert dto.state == 's'
    assert dto.error is None

def test_external_tool_connection_dto() -> None:
    now = datetime.now()
    dto = ExternalToolConnectionDTO(
        id='cid', user_id='uid', provider_id='pid', provider_type=ExternalToolType.GITHUB,
        account_name='acc', account_email='a@b.com', account_id='aid', is_active=True, meta_data={},
        created_at=now, updated_at=now, last_used_at=now, expires_at=now
    )
    assert dto.id == 'cid'
    assert dto.provider_type == ExternalToolType.GITHUB
    assert dto.is_active is True

def test_external_tool_connection_create_dto() -> None:
    now = datetime.now()
    dto = ExternalToolConnectionCreateDTO(
        user_id='uid', provider_id='pid', access_token='tok', refresh_token='rtok',
        account_name='acc', account_email='a@b.com', account_id='aid', meta_data={}, expires_at=now
    )
    assert dto.user_id == 'uid'
    assert dto.access_token == 'tok'

def test_external_resource_dto() -> None:
    now = datetime.now()
    dto = ExternalResourceDTO(
        id='rid', connection_id='cid', resource_id='resid', name='file', type='file',
        url=TypeAdapter(HttpUrl).validate_python('https://file/'), path='/file', size=123, last_modified=now, meta_data={}
    )
    assert dto.id == 'rid'
    assert dto.name == 'file'

def test_external_resource_sync_dto() -> None:
    dto = ExternalResourceSyncDTO(
        connection_id='cid', resource_id='rid', project_id='pid', target_folder_id='fid',
        sync_direction='download', auto_sync=True, sync_interval=10
    )
    assert dto.connection_id == 'cid'
    assert dto.sync_direction == 'download'
    assert dto.auto_sync is True
    assert dto.sync_interval == 10 