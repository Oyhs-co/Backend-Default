from api.shared.models.project import Project, ProjectMember, Task, TaskComment, ActivityLog
from datetime import datetime

def test_project_model_instantiation():
    project = Project(id='pid', name='Project', status='planning', owner_id='uid', created_at=datetime.now())
    assert project.name == 'Project'
    assert project.status == 'planning'
    assert project.owner_id == 'uid'

def test_project_member_model_instantiation():
    member = ProjectMember(id='mid', project_id='pid', user_id='uid', role='member', joined_at=datetime.now())
    assert member.project_id == 'pid'
    assert member.user_id == 'uid'
    assert member.role == 'member'

def test_task_model_instantiation():
    task = Task(id='tid', title='Task', project_id='pid', creator_id='uid', priority='medium', status='todo', created_at=datetime.now())
    assert task.title == 'Task'
    assert task.project_id == 'pid'
    assert task.priority == 'medium'
    assert task.status == 'todo'

def test_task_comment_model_instantiation():
    comment = TaskComment(id='cid', task_id='tid', user_id='uid', content='Comment', created_at=datetime.now())
    assert comment.task_id == 'tid'
    assert comment.user_id == 'uid'
    assert comment.content == 'Comment'

def test_activity_log_model_instantiation():
    log = ActivityLog(id='aid', project_id='pid', user_id='uid', action='create', entity_type='project', entity_id='pid', created_at=datetime.now())
    assert log.project_id == 'pid'
    assert log.action == 'create'
    assert log.entity_type == 'project'
    assert log.entity_id == 'pid' 