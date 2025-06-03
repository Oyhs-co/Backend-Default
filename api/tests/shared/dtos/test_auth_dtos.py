import pytest
from api.shared.dtos.auth_dtos import (
    UserRegisterDTO, UserLoginDTO, TokenDTO, UserProfileDTO, RolePermissionDTO
)
from datetime import datetime

def test_user_register_dto_valid():
    dto = UserRegisterDTO(email='a@b.com', password='12345678', full_name='Name')
    assert dto.email == 'a@b.com'
    assert dto.full_name == 'Name'
    assert dto.company_name is None

def test_user_register_dto_invalid_password():
    with pytest.raises(Exception):
        UserRegisterDTO(email='a@b.com', password='123', full_name='Name')

def test_user_login_dto():
    dto = UserLoginDTO(email='a@b.com', password='12345678')
    assert dto.email == 'a@b.com'
    assert dto.password == '12345678'

def test_token_dto():
    now = datetime.now()
    dto = TokenDTO(access_token='a', refresh_token='b', expires_at=now)
    assert dto.access_token == 'a'
    assert dto.refresh_token == 'b'
    assert dto.token_type == 'bearer'
    assert dto.expires_at == now

def test_user_profile_dto():
    now = datetime.now()
    dto = UserProfileDTO(
        id='id', email='a@b.com', full_name='Name', company_name='C', role='user', created_at=now
    )
    assert dto.id == 'id'
    assert dto.email == 'a@b.com'
    assert dto.full_name == 'Name'
    assert dto.company_name == 'C'
    assert dto.role == 'user'
    assert dto.created_at == now
    assert dto.updated_at is None

def test_role_permission_dto():
    dto = RolePermissionDTO(role='admin', permissions=['read', 'write'])
    assert dto.role == 'admin'
    assert 'read' in dto.permissions 