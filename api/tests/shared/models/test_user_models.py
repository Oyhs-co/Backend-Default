from api.shared.models.user import User, Role, RolePermission
from datetime import datetime

def test_user_model_instantiation():
    user = User(
        id='uid', email='a@b.com', full_name='Name', company_name='C',
        is_active=True, is_verified=False, supabase_uid='supabase-uid', created_at=datetime.now()
    )
    assert user.email == 'a@b.com'
    assert user.full_name == 'Name'
    assert user.is_active is True
    assert user.is_verified is False
    assert user.supabase_uid == 'supabase-uid'

def test_role_model_instantiation():
    role = Role(id='rid', name='admin', description='Admin role', created_at=datetime.now())
    assert role.name == 'admin'
    assert role.description == 'Admin role'

def test_role_permission_model_instantiation():
    perm = RolePermission(id='pid', role_id='rid', resource='project', action='read', created_at=datetime.now())
    assert perm.role_id == 'rid'
    assert perm.resource == 'project'
    assert perm.action == 'read'
    assert perm.conditions is None

def test_user_to_dict():
    user = User(
        id='uid', email='a@b.com', full_name='Name', company_name='C',
        is_active=True, is_verified=True, supabase_uid='supabase-uid', created_at=datetime.now()
    )
    d = user.to_dict()
    assert d['email'] == 'a@b.com'
    assert d['is_verified'] is True 