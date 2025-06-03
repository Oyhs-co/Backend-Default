import pytest
from unittest.mock import MagicMock, patch
from api.project_service.app.services.task_service import TaskService
from api.project_service.app.schemas.task import TaskCreateDTO
from api.shared.exceptions.project_exceptions import TaskNotFoundException, NotProjectMemberException, InsufficientProjectRoleException, ProjectNotFoundException
from datetime import datetime

@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()

@pytest.fixture
def task_service(mock_db: MagicMock) -> TaskService:
    service = TaskService(mock_db)
    service.activity_service = MagicMock()
    return service

def test_create_task_success(task_service: TaskService) -> None:
    task_data = TaskCreateDTO(title="Task1")
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.project.TaskComment", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch.object(task_service, "_task_to_dto", return_value=MagicMock(id="task1")), \
         patch.object(task_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        task_service.db.add = MagicMock()
        task_service.db.commit = MagicMock()
        task_service.db.refresh = MagicMock()
        result = task_service.create_task("proj1", task_data, "user1")
        assert result.id == "task1"

def test_get_task_not_found(task_service: TaskService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.project.TaskComment", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch.object(task_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ProjectNotFoundException):
            task_service.get_task("proj1", "task1", "user1")

def test_update_task_not_member(task_service: TaskService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.project.TaskComment", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch.object(task_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        with pytest.raises(InsufficientProjectRoleException):
            task_service.update_task("proj1", "task1", MagicMock(), "user1")

def test_delete_task_success(task_service: TaskService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.project.TaskComment", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch.object(task_service.db, "query") as mock_query, \
         patch.object(task_service, "_task_to_dto", return_value=MagicMock(id="task1")):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock(creator_id="user1")
        task_service.db.delete = MagicMock()
        task_service.db.commit = MagicMock()
        result = task_service.delete_task("proj1", "task1", "user1")
        assert "message" in result 