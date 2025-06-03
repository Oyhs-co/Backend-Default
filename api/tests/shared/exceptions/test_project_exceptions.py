import pytest
from api.shared.exceptions.project_exceptions import (
    ProjectNotFoundException, TaskNotFoundException, ProjectMemberNotFoundException,
    NotProjectMemberException, InsufficientProjectRoleException, ProjectLimitExceededException,
    TaskLimitExceededException, InvalidTaskStatusTransitionException
)

def test_project_not_found() -> None:
    exc = ProjectNotFoundException()
    assert exc.status_code == 404
    assert exc.detail['message'] == 'Project not found'
    assert exc.detail['error_code'] == 'PROJECT_NOT_FOUND'

def test_task_not_found() -> None:
    exc = TaskNotFoundException()
    assert exc.status_code == 404
    assert exc.detail['message'] == 'Task not found'
    assert exc.detail['error_code'] == 'TASK_NOT_FOUND'

def test_project_member_not_found() -> None:
    exc = ProjectMemberNotFoundException()
    assert exc.status_code == 404
    assert exc.detail['message'] == 'Project member not found'
    assert exc.detail['error_code'] == 'PROJECT_MEMBER_NOT_FOUND'

def test_not_project_member() -> None:
    exc = NotProjectMemberException()
    assert exc.status_code == 403
    assert exc.detail['message'] == 'User is not a member of this project'
    assert exc.detail['error_code'] == 'NOT_PROJECT_MEMBER'

def test_insufficient_project_role() -> None:
    exc = InsufficientProjectRoleException()
    assert exc.status_code == 403
    assert exc.detail['message'] == 'Insufficient project role'
    assert exc.detail['error_code'] == 'INSUFFICIENT_PROJECT_ROLE'

def test_project_limit_exceeded() -> None:
    exc = ProjectLimitExceededException()
    assert exc.status_code == 400
    assert exc.detail['message'] == 'Project limit exceeded'
    assert exc.detail['error_code'] == 'PROJECT_LIMIT_EXCEEDED'

def test_task_limit_exceeded() -> None:
    exc = TaskLimitExceededException()
    assert exc.status_code == 400
    assert exc.detail['message'] == 'Task limit exceeded'
    assert exc.detail['error_code'] == 'TASK_LIMIT_EXCEEDED'

def test_invalid_task_status_transition() -> None:
    exc = InvalidTaskStatusTransitionException()
    assert exc.status_code == 400
    assert exc.detail['message'] == 'Invalid task status transition'
    assert exc.detail['error_code'] == 'INVALID_TASK_STATUS_TRANSITION' 