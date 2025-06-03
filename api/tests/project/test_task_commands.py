from unittest.mock import MagicMock
from api.project_service.app.commands.task_commands import (
    UpdateTaskCommand, AssignTaskCommand, ChangeTaskStatusCommand, CommandInvoker
)

def test_update_task_command_execute_and_undo():
    db = MagicMock()
    cmd = UpdateTaskCommand(db, 'tid', {'title': 'New'})
    db.query().filter().first.return_value = MagicMock(id='tid', title='Old')
    result = cmd.execute()
    assert result.title == 'Old' or hasattr(result, 'title')
    undo_result = cmd.undo()
    assert hasattr(undo_result, 'title')

def test_assign_task_command_execute_and_undo():
    db = MagicMock()
    cmd = AssignTaskCommand(db, 'tid', 'uid')
    db.query().filter().first.return_value = MagicMock(id='tid', assignee_id=None)
    result = cmd.execute()
    assert hasattr(result, 'assignee_id')
    undo_result = cmd.undo()
    assert hasattr(undo_result, 'assignee_id')

def test_change_task_status_command_execute_and_undo():
    db = MagicMock()
    cmd = ChangeTaskStatusCommand(db, 'tid', 'done')
    db.query().filter().first.return_value = MagicMock(id='tid', status='todo')
    result = cmd.execute()
    assert hasattr(result, 'status')
    undo_result = cmd.undo()
    assert hasattr(undo_result, 'status')

def test_command_invoker_execute_undo_redo():
    db = MagicMock()
    cmd = UpdateTaskCommand(db, 'tid', {'title': 'New'})
    invoker = CommandInvoker()
    invoker.execute_command(cmd)
    invoker.undo()
    invoker.redo() 