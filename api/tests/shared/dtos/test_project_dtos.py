import pytest
from api.shared.dtos.project_dtos import (
    ProjectStatus, TaskPriority, TaskStatus,
    ProjectCreateDTO, ProjectUpdateDTO, ProjectResponseDTO,
    TaskCreateDTO, TaskUpdateDTO, TaskResponseDTO,
    ProjectMemberCreateDTO, ProjectMemberUpdateDTO, ProjectMemberResponseDTO,
    ActivityLogDTO
)
from datetime import datetime

def test_project_status_enum() -> None:
    assert ProjectStatus.PLANNING.value == 'planning'
    assert ProjectStatus.COMPLETED.value == 'completed'

def test_task_priority_enum() -> None:
    assert TaskPriority.LOW.value == 'low'
    assert TaskPriority.URGENT.value == 'urgent'

def test_task_status_enum() -> None:
    assert TaskStatus.TODO.value == 'todo'
    assert TaskStatus.DONE.value == 'done'

def test_project_create_dto_valid() -> None:
    dto = ProjectCreateDTO(name='Project', status=ProjectStatus.PLANNING)
    assert dto.name == 'Project'
    assert dto.status == ProjectStatus.PLANNING
    assert dto.tags is None
    assert dto.metadata is None

def test_project_create_dto_invalid_name() -> None:
    with pytest.raises(Exception):
        ProjectCreateDTO(name='ab', status=ProjectStatus.PLANNING)

def test_project_update_dto() -> None:
    dto = ProjectUpdateDTO(name='New', tags=['a'], metadata={'k': 1})
    assert dto.name == 'New'
    assert dto.tags == ['a']
    assert dto.metadata == {'k': 1}

def test_project_response_dto() -> None:
    now = datetime.now()
    dto = ProjectResponseDTO(
        id='id', name='n', status=ProjectStatus.PLANNING, owner_id='uid', created_at=now
    )
    assert dto.id == 'id'
    assert dto.status == ProjectStatus.PLANNING
    assert dto.created_at == now

def test_task_create_dto() -> None:
    dto = TaskCreateDTO(title='Task', project_id='pid')
    assert dto.title == 'Task'
    assert dto.project_id == 'pid'
    assert dto.priority == TaskPriority.MEDIUM
    assert dto.status == TaskStatus.TODO

def test_task_update_dto() -> None:
    dto = TaskUpdateDTO(title='Title', priority=TaskPriority.HIGH)
    assert dto.title == 'Title'
    assert dto.priority == TaskPriority.HIGH

def test_task_response_dto() -> None:
    now = datetime.now()
    dto = TaskResponseDTO(
        id='id', title='t', project_id='pid', creator_id='uid', priority=TaskPriority.LOW, status=TaskStatus.TODO, created_at=now
    )
    assert dto.id == 'id'
    assert dto.priority == TaskPriority.LOW
    assert dto.status == TaskStatus.TODO

def test_project_member_create_dto() -> None:
    dto = ProjectMemberCreateDTO(project_id='pid', user_id='uid')
    assert dto.role == 'member'

def test_project_member_update_dto() -> None:
    dto = ProjectMemberUpdateDTO(role='admin')
    assert dto.role == 'admin'

def test_project_member_response_dto() -> None:
    now = datetime.now()
    dto = ProjectMemberResponseDTO(id='id', project_id='pid', user_id='uid', role='member', joined_at=now)
    assert dto.id == 'id'
    assert dto.role == 'member'
    assert dto.joined_at == now

def test_activity_log_dto() -> None:
    now = datetime.now()
    dto = ActivityLogDTO(id='id', project_id='pid', user_id='uid', action='act', entity_type='project', entity_id='eid', created_at=now)
    assert dto.id == 'id'
    assert dto.action == 'act' 