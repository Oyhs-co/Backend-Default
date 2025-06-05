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

def test_document_create_dto_invalid():
    try:
        DocumentCreateDTO(name="", project_id="proj1", type="file")
    except Exception as e:
        assert isinstance(e, Exception)

def test_document_update_dto():
    dto = DocumentUpdateDTO(name='New', tags=['a'], meta_data={'k': 1})
    assert dto.name == 'New'
    assert dto.tags == ['a']
    assert dto.meta_data == {'k': 1}

def test_document_type_enum():
    assert DocumentType.FILE.value == 'file'
    assert DocumentType.FOLDER.value == 'folder'
    assert DocumentType.LINK.value == 'link'

def test_document_response_dto_valid():
    dto = DocumentResponseDTO(
        id="doc1",
        name="TestDoc",
        project_id="proj1",
        parent_id=None,
        type="file",
        content_type="application/pdf",
        size=123,
        url="http://url",
        description="desc",
        version=1,
        creator_id="user1",
        tags=["tag1"],
        meta_data={"k": "v"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert dto.id == "doc1"

def test_document_version_dto():
    dto = DocumentVersionDTO(
        id="ver1",
        document_id="doc1",
        version=1,
        size=123,
        content_type="application/pdf",
        url="http://url",
        creator_id="user1",
        changes="cambios",
        created_at=datetime.now(),
    )
    assert dto.id == "ver1"

def test_document_permission_dto_valid():
    dto = DocumentPermissionDTO(
        id="perm1",
        document_id="doc1",
        user_id="user1",
        role_id=None,
        can_view=True,
        can_edit=False,
        can_delete=False,
        can_share=False,
        created_at=datetime.now(),
        updated_at=None,
    )
    assert dto.id == "perm1"

def test_document_permission_create_dto_defaults():
    dto = DocumentPermissionCreateDTO()
    assert dto.can_view is True
    assert dto.can_edit is False

def test_document_permission_update_dto_partial():
    dto = DocumentPermissionUpdateDTO(can_edit=True)
    assert dto.can_edit is True

def test_document_upload_response_dto():
    doc = DocumentResponseDTO(
        id="doc1",
        name="TestDoc",
        project_id="proj1",
        parent_id=None,
        type="file",
        content_type="application/pdf",
        size=123,
        url="http://url",
        description="desc",
        version=1,
        creator_id="user1",
        tags=["tag1"],
        meta_data={"k": "v"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    dto = DocumentUploadResponseDTO(document=doc, upload_url="http://upload")
    assert dto.upload_url == "http://upload" 