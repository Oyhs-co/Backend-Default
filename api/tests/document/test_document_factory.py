import pytest
from api.document_service.app.factories.document_factory import DocumentFactory
from api.document_service.app.schemas.document import DocumentType
from api.shared.exceptions.document_exceptions import InvalidDocumentTypeException

@pytest.fixture
def factory() -> DocumentFactory:
    return DocumentFactory()

def test_create_file_document(factory: DocumentFactory) -> None:
    doc = factory.create_document(
        document_type=DocumentType.FILE,
        name='file1',
        project_id='pid',
        creator_id='uid',
        content_type='text/plain',
        url='http://file',
        tags=['tag'],
        meta_data={'k': 'v'}
    )
    assert doc.type == DocumentType.FILE
    assert doc.name == 'file1'
    assert doc.content_type == 'text/plain'
    assert doc.url == 'http://file'
    assert doc.tags == ['tag']
    assert doc.meta_data == {'k': 'v'}

def test_create_folder_document(factory: DocumentFactory) -> None:
    doc = factory.create_document(
        document_type=DocumentType.FOLDER,
        name='folder1',
        project_id='pid',
        creator_id='uid',
        tags=['tag2'],
        meta_data={'folder': True}
    )
    assert doc.type == DocumentType.FOLDER
    assert doc.name == 'folder1'
    assert doc.tags == ['tag2']
    assert doc.meta_data == {'folder': True}

def test_create_link_document(factory: DocumentFactory) -> None:
    doc = factory.create_document(
        document_type=DocumentType.LINK,
        name='link1',
        project_id='pid',
        creator_id='uid',
        url='http://link',
        tags=['tag3'],
        meta_data={'link': True}
    )
    assert doc.type == DocumentType.LINK
    assert doc.url == 'http://link'
    assert doc.tags == ['tag3']
    assert doc.meta_data == {'link': True}

def test_create_link_document_without_url_raises(factory: DocumentFactory) -> None:
    with pytest.raises(InvalidDocumentTypeException):
        factory.create_document(
            document_type=DocumentType.LINK,
            name='link2',
            project_id='pid',
            creator_id='uid',
        )

def test_create_invalid_type_raises(factory: DocumentFactory) -> None:
    with pytest.raises(InvalidDocumentTypeException):
        factory.create_document(
            document_type='invalid',  # type: ignore
            name='bad',
            project_id='pid',
            creator_id='uid',
        ) 