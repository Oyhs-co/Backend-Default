import pytest
from api.document_service.app.schemas.document import (
    DocumentCreateDTO, DocumentUpdateDTO, DocumentType, DocumentResponseDTO, DocumentVersionDTO,
    DocumentPermissionDTO, DocumentPermissionCreateDTO, DocumentPermissionUpdateDTO, DocumentUploadResponseDTO
)
from datetime import datetime

def test_document_create_dto_valid():
    dto = DocumentCreateDTO(
        name='Doc', project_id='pid', type=DocumentType.FILE
    )
    assert dto.name == 'Doc'
    assert dto.type == DocumentType.FILE

def test_document_create_dto_invalid_name():
    with pytest.raises(Exception):
        DocumentCreateDTO(name='', project_id='pid', type=DocumentType.FILE)

def test_document_update_dto():
    dto = DocumentUpdateDTO(name='New', tags=['a'], meta_data={'k': 1})
    assert dto.name == 'New'
    assert dto.tags == ['a']
    assert dto.meta_data == {'k': 1}

def test_document_type_enum():
    assert DocumentType.FILE.value == 'file'
    assert DocumentType.FOLDER.value == 'folder'
    assert DocumentType.LINK.value == 'link'

def test_document_response_dto():
    dto = DocumentResponseDTO(
        id='id', name='n', project_id='pid', type=DocumentType.FILE, version=1, creator_id='uid',
        created_at=datetime.now()
    )
    assert dto.id == 'id'
    assert dto.type == DocumentType.FILE

def test_document_version_dto():
    dto = DocumentVersionDTO(
        id='id', document_id='doc', version=1, creator_id='uid', created_at=datetime.now()
    )
    assert dto.version == 1

def test_document_permission_dto():
    dto = DocumentPermissionDTO(
        id='id', document_id='doc', can_view=True, can_edit=False, can_delete=False, can_share=False, created_at=datetime.now()
    )
    assert dto.can_view is True

def test_document_permission_create_dto():
    dto = DocumentPermissionCreateDTO(can_edit=True)
    assert dto.can_edit is True

def test_document_permission_update_dto():
    dto = DocumentPermissionUpdateDTO(can_share=True)
    assert dto.can_share is True

def test_document_upload_response_dto():
    doc = DocumentResponseDTO(
        id='id', name='n', project_id='pid', type=DocumentType.FILE, version=1, creator_id='uid', created_at=datetime.now()
    )
    dto = DocumentUploadResponseDTO(document=doc, upload_url='http://url')
    assert dto.upload_url == 'http://url' 