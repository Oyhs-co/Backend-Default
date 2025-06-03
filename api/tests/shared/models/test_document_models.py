from api.shared.models.document import Document, DocumentVersion, DocumentPermission
from datetime import datetime

def test_document_model_instantiation():
    doc = Document(
        id='did', name='Doc', project_id='pid', type='file', creator_id='uid', version=1, created_at=datetime.now()
    )
    assert doc.name == 'Doc'
    assert doc.project_id == 'pid'
    assert doc.type == 'file'
    assert doc.version == 1
    assert doc.creator_id == 'uid'

def test_document_version_model_instantiation():
    ver = DocumentVersion(
        id='vid', document_id='did', version=1, creator_id='uid', created_at=datetime.now()
    )
    assert ver.document_id == 'did'
    assert ver.version == 1
    assert ver.creator_id == 'uid'

def test_document_permission_model_instantiation():
    perm = DocumentPermission(
        id='pid', document_id='did', user_id='uid', can_view=True, can_edit=False, can_delete=False, can_share=False, created_at=datetime.now()
    )
    assert perm.document_id == 'did'
    assert perm.user_id == 'uid'
    assert perm.can_view is True
    assert perm.can_edit is False
    assert perm.can_delete is False
    assert perm.can_share is False 