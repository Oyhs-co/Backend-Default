from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from api.shared.models.project import Task
from api.shared.exceptions.project_exceptions import TaskNotFoundException


class Command(ABC):
    """Abstract command interface"""

    @abstractmethod
    def execute(self) -> Any:
        """Execute the command"""
        pass

    @abstractmethod
    def undo(self) -> Any:
        """Undo the command"""
        pass


class TaskCommand(Command):
    """Base task command"""

    def __init__(self, db: Session, task_id: str):
        """
        Initialize TaskCommand.

        Args:
            db (Session): Database session
            task_id (str): Task ID
        """
        self.db = db
        self.task_id = task_id
        self.task = self._get_task()
        self.previous_state = self._get_task_state()

    def _get_task(self) -> Task:
        """
        Get task.

        Returns:
            Task: Task

        Raises:
            TaskNotFoundException: If task not found
        """
        task = self.db.query(Task).filter(Task.id == self.task_id).first()

        if not task:
            raise TaskNotFoundException()

        return task

    def _get_task_state(self) -> Dict[str, Any]:
        """
        Get task state.

        Returns:
            Dict[str, Any]: Task state
        """
        return {
            "title": self.task.title,
            "description": self.task.description,
            "assignee_id": self.task.assignee_id,
            "due_date": self.task.due_date,
            "priority": self.task.priority,
            "status": self.task.status,
            "tags": self.task.tags,
            "metadata": self.task.metadata
        }


class UpdateTaskCommand(TaskCommand):
    """Command to update a task"""

    def __init__(self, db: Session, task_id: str, updates: Dict[str, Any]):
        """
        Initialize UpdateTaskCommand.

        Args:
            db (Session): Database session
            task_id (str): Task ID
            updates (Dict[str, Any]): Task updates
        """
        super().__init__(db, task_id)
        self.updates = updates

    def execute(self) -> Task:
        """
        Execute the command.

        Returns:
            Task: Updated task
        """
        # Update task
        for key, value in self.updates.items():
            if hasattr(self.task, key):
                setattr(self.task, key, value)

        # Update task in database
        self.task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(self.task)

        return self.task

    def undo(self) -> Task:
        """
        Undo the command.

        Returns:
            Task: Restored task
        """
        # Restore task state
        for key, value in self.previous_state.items():
            if hasattr(self.task, key):
                setattr(self.task, key, value)

        # Update task in database
        self.task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(self.task)

        return self.task


class AssignTaskCommand(TaskCommand):
    """Command to assign a task"""

    def __init__(self, db: Session, task_id: str, assignee_id: Optional[str]):
        """
        Initialize AssignTaskCommand.

        Args:
            db (Session): Database session
            task_id (str): Task ID
            assignee_id (Optional[str]): Assignee ID
        """
        super().__init__(db, task_id)
        self.assignee_id = assignee_id

    def execute(self) -> Task:
        """
        Execute the command.

        Returns:
            Task: Updated task
        """
        # Update task
        self.task.assignee_id = self.assignee_id

        # Update task in database
        self.task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(self.task)

        return self.task

    def undo(self) -> Task:
        """
        Undo the command.

        Returns:
            Task: Restored task
        """
        # Restore task state
        self.task.assignee_id = self.previous_state["assignee_id"]

        # Update task in database
        self.task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(self.task)

        return self.task


class ChangeTaskStatusCommand(TaskCommand):
    """Command to change task status"""

    def __init__(self, db: Session, task_id: str, status: str):
        """
        Initialize ChangeTaskStatusCommand.

        Args:
            db (Session): Database session
            task_id (str): Task ID
            status (str): Task status
        """
        super().__init__(db, task_id)
        self.status = status

    def execute(self) -> Task:
        """
        Execute the command.

        Returns:
            Task: Updated task
        """
        # Update task
        self.task.status = self.status

        # Update task in database
        self.task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(self.task)

        return self.task

    def undo(self) -> Task:
        """
        Undo the command.

        Returns:
            Task: Restored task
        """
        # Restore task state
        self.task.status = self.previous_state["status"]

        # Update task in database
        self.task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(self.task)

        return self.task


class CommandInvoker:
    """Command invoker"""

    def __init__(self):
        """Initialize CommandInvoker"""
        self.history: List[Command] = []
        self.undo_history: List[Command] = []

    def execute_command(self, command: Command) -> Any:
        """
        Execute a command.

        Args:
            command (Command): Command to execute

        Returns:
            Any: Command result
        """
        result = command.execute()
        self.history.append(command)
        self.undo_history = []
        return result

    def undo(self) -> Any:
        """
        Undo the last command.

        Returns:
            Any: Command result

        Raises:
            Exception: If no commands to undo
        """
        if not self.history:
            raise Exception("No commands to undo")

        command = self.history.pop()
        result = command.undo()
        self.undo_history.append(command)
        return result

    def redo(self) -> Any:
        """
        Redo the last undone command.

        Returns:
            Any: Command result

        Raises:
            Exception: If no commands to redo
        """
        if not self.undo_history:
            raise Exception("No commands to redo")

        command = self.undo_history.pop()
        result = command.execute()
        self.history.append(command)
        return result