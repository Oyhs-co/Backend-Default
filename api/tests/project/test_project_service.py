import pytest
from unittest.mock import MagicMock, patch
from api.project_service.app.services.project_service import ProjectService
from api.project_service.app.schemas.project import ProjectCreateDTO
from api.shared.exceptions.project_exceptions import ProjectNotFoundException, NotProjectMemberException

@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()

@pytest.fixture
def project_service(mock_db: MagicMock) -> ProjectService:
    return ProjectService(mock_db)

def test_create_project_success(project_service: ProjectService):
    project_data = ProjectCreateDTO(name="Project1")
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service, "_project_to_dto", return_value=MagicMock(id="proj1")), \
         patch.object(project_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None  # No duplicate project
        project_service.db.add = MagicMock()
        project_service.db.commit = MagicMock()
        project_service.db.refresh = MagicMock()
        result = project_service.create_project(project_data, "user1")
        assert result.id == "proj1"

def test_get_project_not_found(project_service: ProjectService):
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ProjectNotFoundException):
            project_service.get_project("proj1", "user1")

def test_update_project_not_member(project_service: ProjectService):
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query, \
         patch.object(project_service, "_has_permission", return_value=False):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        with pytest.raises(NotProjectMemberException):
            project_service.update_project("proj1", MagicMock(), "user1")

def test_delete_project_success(project_service: ProjectService):
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query, \
         patch.object(project_service, "_has_permission", return_value=True), \
         patch.object(project_service, "_project_to_dto", return_value=MagicMock(id="proj1")):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock(owner_id="user1")
        project_service.db.delete = MagicMock()
        project_service.db.commit = MagicMock()
        result = project_service.delete_project("proj1", "user1")
        assert "message" in result 