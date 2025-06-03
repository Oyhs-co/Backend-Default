import pytest
from unittest.mock import MagicMock, patch
from api.document_service.app.services.document_service import DocumentService
from api.document_service.app.schemas.document import DocumentCreateDTO, DocumentType
from api.shared.exceptions.document_exceptions import DocumentNotFoundException, InsufficientDocumentPermissionException

@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()

@pytest.fixture
def document_service(mock_db: MagicMock) -> DocumentService:
    return DocumentService(mock_db)

def test_create_document_success(document_service: DocumentService):
    doc_data = DocumentCreateDTO(
        name="Doc1",
        project_id="proj1",
        type=DocumentType.FILE
    )
    with patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.document.DocumentPermission", MagicMock()), \
         patch("api.shared.models.document.DocumentVersion", MagicMock()), \
         patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch("api.shared.models.user.User", MagicMock()), \
         patch.object(document_service.db, "query") as mock_query, \
         patch.object(document_service, "_has_permission", return_value=True), \
         patch.object(document_service, "_document_to_dto", return_value=MagicMock(id="doc1")):
        mock_project = MagicMock()
        mock_member = MagicMock()
        mock_query.return_value.filter.return_value.first.side_effect = [mock_project, mock_member]
        document_service.db.add = MagicMock()
        document_service.db.commit = MagicMock()
        document_service.db.refresh = MagicMock()
        result = document_service.create_document(doc_data, "user1")
        assert result.id == "doc1"

def test_get_document_not_found(document_service: DocumentService):
    with patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.document.DocumentPermission", MagicMock()), \
         patch("api.shared.models.document.DocumentVersion", MagicMock()), \
         patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(document_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(DocumentNotFoundException):
            document_service.get_document("doc1", "user1")

def test_update_document_permission_denied(document_service: DocumentService):
    with patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.document.DocumentPermission", MagicMock()), \
         patch("api.shared.models.document.DocumentVersion", MagicMock()), \
         patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(document_service.db, "query") as mock_query, \
         patch.object(document_service, "_has_permission", return_value=False):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        with pytest.raises(InsufficientDocumentPermissionException):
            document_service.update_document("doc1", MagicMock(), "user1")

def test_delete_document_success(document_service: DocumentService):
    with patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.document.DocumentPermission", MagicMock()), \
         patch("api.shared.models.document.DocumentVersion", MagicMock()), \
         patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(document_service.db, "query") as mock_query, \
         patch.object(document_service, "_has_permission", return_value=True), \
         patch.object(document_service, "_document_to_dto", return_value=MagicMock(id="doc1")):
        mock_doc = MagicMock(type=DocumentType.FILE, url=None, creator_id="user1")
        mock_query.return_value.filter.return_value.first.return_value = mock_doc
        document_service.db.delete = MagicMock()
        document_service.db.commit = MagicMock()
        result = document_service.delete_document("doc1", "user1")
        assert "message" in result 