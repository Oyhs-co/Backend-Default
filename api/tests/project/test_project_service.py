import pytest
from unittest.mock import MagicMock, patch
from api.project_service.app.services.project_service import ProjectService
from api.project_service.app.schemas.project import ProjectCreateDTO, ProjectUpdateDTO, ProjectMemberCreateDTO, ProjectMemberUpdateDTO
from api.shared.exceptions.project_exceptions import ProjectNotFoundException, InsufficientProjectRoleException
from datetime import datetime

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def project_service(mock_db):
    return ProjectService(mock_db)

def test_create_project_success(project_service: ProjectService) -> None:
    project_data = ProjectCreateDTO(name="Project1")
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service, "_project_to_dto", return_value=MagicMock(id="proj1")), \
         patch.object(project_service.db, "query") as mock_query, \
         patch.object(project_service, "activity_service", create=True) as mock_activity_service, \
         patch.object(project_service.db, "add", MagicMock()), \
         patch.object(project_service.db, "commit", MagicMock()), \
         patch.object(project_service.db, "refresh", MagicMock()):
        mock_query.return_value.filter.return_value.first.return_value = None  # No duplicate project
        # Patch log_activity to return a valid ActivityLogResponseDTO
        mock_activity_service.log_activity.return_value = MagicMock(
            id="aid", project_id="pid", user_id="user1", action="create", entity_type="project", entity_id="pid", details=None, created_at=datetime.now()
        )
        result = project_service.create_project(project_data, "user1")
        assert result.id == "proj1"

def test_get_project_not_found(project_service: ProjectService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ProjectNotFoundException):
            project_service.get_project("proj1", "user1")

def test_update_project_not_member(project_service: ProjectService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        with pytest.raises(InsufficientProjectRoleException):
            project_service.update_project("proj1", MagicMock(), "user1")

def test_delete_project_success(project_service: ProjectService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query, \
         patch.object(project_service, "_project_to_dto", return_value=MagicMock(id="proj1")), \
         patch.object(project_service.db, "delete", MagicMock()), \
         patch.object(project_service.db, "commit", MagicMock()):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock(owner_id="not_owner")
        with pytest.raises(InsufficientProjectRoleException):
            project_service.delete_project("proj1", "user1")

def test_delete_project_not_found(project_service: ProjectService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ProjectNotFoundException):
            project_service.delete_project("proj1", "user1")

def test_update_project_invalid_data(project_service: ProjectService) -> None:
    with pytest.raises(Exception):
        ProjectUpdateDTO(name="ab")

def test_create_project_duplicate_name(project_service: ProjectService) -> None:
    project_data = ProjectCreateDTO(name="Project1")
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        with pytest.raises(Exception):
            project_service.create_project(project_data, "user1")

def test_add_project_member_success(project_service: ProjectService):
    member_data = ProjectMemberCreateDTO(user_id="user2", role="member")
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query, \
         patch.object(project_service, "activity_service", create=True) as mock_activity_service, \
         patch.object(project_service, "_project_member_to_dto", return_value=MagicMock(id="mem1")), \
         patch.object(project_service.db, "add", MagicMock()), \
         patch.object(project_service.db, "commit", MagicMock()), \
         patch.object(project_service.db, "refresh", MagicMock()):
        # Simular proyecto y miembro actual con rol owner
        mock_query.return_value.filter.return_value.first.side_effect = [MagicMock(), MagicMock(role="owner"), None]
        mock_activity_service.log_activity.return_value = MagicMock()
        result = project_service.add_project_member("proj1", member_data, "user1")
        assert result.id == "mem1"

def test_add_project_member_insufficient_role(project_service: ProjectService):
    member_data = ProjectMemberCreateDTO(user_id="user2", role="member")
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query:
        # Simular proyecto y miembro actual con rol member (no owner/admin)
        mock_query.return_value.filter.return_value.first.side_effect = [MagicMock(), MagicMock(role="member")]
        with pytest.raises(InsufficientProjectRoleException):
            project_service.add_project_member("proj1", member_data, "user1")

def test_update_project_member_success(project_service: ProjectService):
    member_data = ProjectMemberUpdateDTO(role="admin")
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query, \
         patch.object(project_service, "activity_service", create=True) as mock_activity_service, \
         patch.object(project_service, "_project_member_to_dto", return_value=MagicMock(id="mem1")), \
         patch.object(project_service.db, "commit", MagicMock()), \
         patch.object(project_service.db, "refresh", MagicMock()):
        # Simular proyecto, miembro actual owner/admin y miembro a actualizar
        mock_query.return_value.filter.return_value.first.side_effect = [MagicMock(), MagicMock(role="owner"), MagicMock(role="member")]
        mock_activity_service.log_activity.return_value = MagicMock()
        result = project_service.update_project_member("proj1", "mem1", member_data, "user1")
        assert result.id == "mem1"

def test_remove_project_member_success(project_service: ProjectService):
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query, \
         patch.object(project_service, "activity_service", create=True) as mock_activity_service, \
         patch.object(project_service.db, "delete", MagicMock()), \
         patch.object(project_service.db, "commit", MagicMock()):
        # Simular proyecto, miembro actual owner/admin y miembro a eliminar
        mock_query.return_value.filter.return_value.first.side_effect = [MagicMock(), MagicMock(role="owner"), MagicMock(role="member")]
        mock_activity_service.log_activity.return_value = MagicMock()
        result = project_service.remove_project_member("proj1", "mem1", "user1")
        assert "message" in result

def test_get_project_members_success(project_service: ProjectService):
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch.object(project_service.db, "query") as mock_query, \
         patch.object(project_service, "_project_member_to_dto", return_value=MagicMock(id="mem1")):
        # Simular proyecto y miembro actual
        mock_query.return_value.filter.return_value.first.side_effect = [MagicMock(), MagicMock(role="owner")]
        mock_query.return_value.filter.return_value.all.return_value = [MagicMock()]
        result = project_service.get_project_members("proj1", "user1")
        assert isinstance(result, list)
        assert result[0].id == "mem1" 