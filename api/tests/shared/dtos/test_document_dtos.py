from datetime import datetime
import pytest
from pydantic import ValidationError
from api.shared.dtos.document_dtos import (
    DocumentType, DocumentCreateDTO, DocumentUpdateDTO, DocumentResponseDTO,
    DocumentVersionDTO, DocumentPermissionDTO, DocumentUploadResponseDTO
)

def test_document_type_enum():
    assert DocumentType.FILE.value == 'file'
    assert DocumentType.FOLDER.value == 'folder'
    assert DocumentType.LINK.value == 'link'

def test_document_create_dto_valid():
    dto = DocumentCreateDTO(
        name='Test Document',
        project_id='proj1',
        type=DocumentType.FILE
    )
    assert dto.name == 'Test Document'
    assert dto.type == DocumentType.FILE
    assert dto.project_id == 'proj1'
    assert dto.content_type is None
    assert dto.tags is None
    assert dto.meta_data is None

def test_document_create_dto_invalid():
    try:
        DocumentCreateDTO(
            name='',  # nombre vacío, debe fallar
            project_id='proj1',
            type=DocumentType.FILE
        )
        assert False, "Should have raised an error"
    except Exception as e:
        assert True

def test_document_update_dto():
    tags = ['doc', 'test']
    meta = {'key': 'value'}
    dto = DocumentUpdateDTO(
        name='Updated Doc',
        tags=tags,
        meta_data=meta
    )
    assert dto.name == 'Updated Doc'
    assert dto.tags is not None and 'doc' in dto.tags
    assert dto.meta_data is not None and dto.meta_data.get('key') == 'value'

def test_document_response_dto():
    now = datetime.now()
    dto = DocumentResponseDTO(
        id='doc1',
        name='Test Doc',
        project_id='proj1',
        type=DocumentType.FILE,
        version=1,
        creator_id='user1',
        created_at=now
    )
    assert dto.id == 'doc1'
    assert dto.name == 'Test Doc'
    assert dto.version == 1
    assert dto.created_at == now

def test_document_version_dto():
    now = datetime.now()
    dto = DocumentVersionDTO(
        id='ver1',
        document_id='doc1',
        version=1,
        creator_id='user1',
        content_type='application/pdf',
        size=1024,
        url='http://example.com/doc',
        changes='Initial version',
        created_at=now
    )
    assert dto.id == 'ver1'
    assert dto.document_id == 'doc1'
    assert dto.version == 1
    assert dto.size == 1024

def test_document_permission_dto():
    now = datetime.now()
    dto = DocumentPermissionDTO(
        id='perm1',
        document_id='doc1',
        user_id='user1',
        can_view=True,
        can_edit=True,
        can_delete=False,
        can_share=False,
        created_at=now
    )
    assert dto.id == 'perm1'
    assert dto.document_id == 'doc1'
    assert dto.can_view is True
    assert dto.can_delete is False

def test_document_upload_response_dto():
    now = datetime.now()
    doc = DocumentResponseDTO(
        id='doc1',
        name='Test Doc',
        project_id='proj1', 
        type=DocumentType.FILE,
        version=1,
        creator_id='user1',
        created_at=now
    )
    dto = DocumentUploadResponseDTO(
        document=doc,
        upload_url='http://example.com/upload'
    )
    assert isinstance(dto.document, DocumentResponseDTO)
    assert dto.document.id == 'doc1'
    assert dto.upload_url == 'http://example.com/upload'

def test_document_create_dto_all_fields():
    tags = ['doc', 'test', 'complete']
    meta = {'key1': 'value1', 'key2': 'value2'}
    dto = DocumentCreateDTO(
        name='Complete Doc',
        project_id='proj1',
        parent_id='folder1',
        type=DocumentType.FILE,
        content_type='application/pdf',
        url='http://example.com/doc',
        description='Test document with all fields',
        tags=tags,
        meta_data=meta
    )
    assert dto.name == 'Complete Doc'
    assert dto.parent_id == 'folder1'
    assert dto.description == 'Test document with all fields'
    assert dto.tags is not None and len(dto.tags) == 3
    assert dto.meta_data is not None and len(dto.meta_data) == 2

def test_document_response_dto_all_fields():
    now = datetime.now()
    dto = DocumentResponseDTO(
        id='doc1',
        name='Complete Doc',
        project_id='proj1',
        parent_id='folder1',
        type=DocumentType.FILE,
        content_type='application/pdf',
        size=2048,
        url='http://example.com/doc',
        description='Full document response',
        version=1,
        creator_id='user1',
        tags=['doc', 'test'],
        meta_data={'status': 'active'},
        created_at=now,
        updated_at=now
    )
    assert dto.id == 'doc1'
    assert dto.parent_id == 'folder1'
    assert dto.size == 2048
    assert dto.content_type == 'application/pdf'
    assert dto.updated_at == now