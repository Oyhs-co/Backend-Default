import pytest
from unittest.mock import MagicMock, patch
from api.project_service.app.services.task_service import TaskService
from api.project_service.app.schemas.task import TaskCreateDTO, TaskCommentCreateDTO
from api.shared.exceptions.project_exceptions import InsufficientProjectRoleException, ProjectNotFoundException

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
         patch.object(task_service.db, "query") as mock_query, \
         patch.object(task_service.db, "add", MagicMock()), \
         patch.object(task_service.db, "commit", MagicMock()), \
         patch.object(task_service.db, "refresh", MagicMock()):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
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
         patch.object(task_service, "_task_to_dto", return_value=MagicMock(id="task1")), \
         patch.object(task_service.db, "delete", MagicMock()), \
         patch.object(task_service.db, "commit", MagicMock()):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock(creator_id="user1")
        result = task_service.delete_task("proj1", "task1", "user1")
        assert "message" in result

def test_delete_task_permission_denied(task_service: TaskService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.project.TaskComment", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch.object(task_service.db, "query") as mock_query, \
         patch.object(task_service, "_task_to_dto", return_value=MagicMock(id="task1")):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock(creator_id="other_user")
        with pytest.raises(InsufficientProjectRoleException):
            task_service.delete_task("proj1", "task1", "user1")

def test_update_task_not_found(task_service: TaskService) -> None:
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.project.TaskComment", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch("api.shared.models.document.Document", MagicMock()), \
         patch.object(task_service.db, "query") as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ProjectNotFoundException):
            task_service.update_task("proj1", "task1", MagicMock(), "user1")

def test_create_task_invalid_data(task_service: TaskService) -> None:
    from api.project_service.app.schemas.task import TaskCreateDTO
    import pytest
    with pytest.raises(Exception):
        TaskCreateDTO(title="")

def test_get_project_tasks(task_service: TaskService):
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch.object(task_service.db, "query") as mock_query, \
         patch.object(task_service, "_task_to_dto", return_value=MagicMock(id="task1")):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        mock_query.return_value.filter.return_value.all.return_value = [MagicMock()]
        result = task_service.get_project_tasks("proj1", "user1")
        assert isinstance(result, list)
        assert result[0].id == "task1"

def test_add_task_comment(task_service: TaskService):
    from api.project_service.app.schemas.task import TaskCommentCreateDTO
    comment_data = TaskCommentCreateDTO(content="Comentario")
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.project.TaskComment", MagicMock()), \
         patch.object(task_service.db, "query") as mock_query, \
         patch.object(task_service, "_task_comment_to_dto", return_value=MagicMock(id="c1")), \
         patch.object(task_service.db, "add"), \
         patch.object(task_service.db, "commit"), \
         patch.object(task_service.db, "refresh"), \
         patch.object(task_service.activity_service, "log_activity"):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        result = task_service.add_task_comment("proj1", "task1", comment_data, "user1")
        assert result.id == "c1"

def test_get_task_comments(task_service: TaskService):
    with patch("api.shared.models.project.Project", MagicMock()), \
         patch("api.shared.models.project.ProjectMember", MagicMock()), \
         patch("api.shared.models.project.Task", MagicMock()), \
         patch("api.shared.models.project.TaskComment", MagicMock()), \
         patch.object(task_service.db, "query") as mock_query, \
         patch.object(task_service, "_task_comment_to_dto", return_value=MagicMock(id="c1")):
        mock_query.return_value.filter.return_value.first.return_value = MagicMock()
        mock_query.return_value.filter.return_value.filter.return_value.first.return_value = MagicMock()
        mock_query.return_value.filter.return_value.all.return_value = [MagicMock()]
        result = task_service.get_task_comments("proj1", "task1", "user1")
        assert isinstance(result, list)
        assert result[0].id == "c1" 