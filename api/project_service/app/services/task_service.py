from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from api.project_service.app.schemas.task import (
    TaskCommentCreateDTO,
    TaskCommentResponseDTO,
    TaskCreateDTO,
    TaskPriority,
    TaskResponseDTO,
    TaskStatus,
    TaskUpdateDTO,
)
from api.project_service.app.services.activity_service import ActivityService
from api.project_service.app.commands.task_commands import ChangeTaskStatusCommand, CommandInvoker
from api.shared.exceptions.project_exceptions import (
    InsufficientProjectRoleException,
    InvalidTaskStatusTransitionException,
    NotProjectMemberException,
    ProjectNotFoundException,
    TaskNotFoundException,
)
from api.shared.models.project import Project, ProjectMember, Task, TaskComment


class TaskService:
    """Service for task operations"""

    def __init__(self, db: Session):
        """
        Initialize TaskService.

        Args:
            db (Session): Database session
        """
        self.db = db
        self.activity_service = ActivityService(db)

    def create_task(
        self, project_id: str, task_data: TaskCreateDTO, user_id: str
    ) -> TaskResponseDTO:
        """
        Create a new task.

        Args:
            project_id (str): Project ID
            task_data (TaskCreateDTO): Task data
            user_id (str): User ID

        Returns:
            TaskResponseDTO: Created task

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Create task
        task = Task(
            title=task_data.title,
            description=task_data.description,
            project_id=project_id,
            creator_id=user_id,
            assignee_id=task_data.assignee_id,
            due_date=task_data.due_date,
            priority=task_data.priority,
            status=task_data.status,
            tags=(task_data.tags or {}),
            meta_data=(task_data.meta_data or {}),
        )

        # Add task to database
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        # Log activity
        self.activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="create_task",
            entity_type="task",
            entity_id=str(task.id),
            details=task_data.model_dump(exclude_none=True),
        )

        # Return task
        return self._task_to_dto(task)

    def get_task(self, project_id: str, task_id: str, user_id: str) -> TaskResponseDTO:
        """
        Get a task.

        Args:
            project_id (str): Project ID
            task_id (str): Task ID
            user_id (str): User ID

        Returns:
            TaskResponseDTO: Task

        Raises:
            ProjectNotFoundException: If project not found
            TaskNotFoundException: If task not found
            NotProjectMemberException: If user is not a project member
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Get task
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )

        # Check if task exists
        if not task:
            raise TaskNotFoundException()

        # Return task
        return self._task_to_dto(task)

    def update_task(
        self, project_id: str, task_id: str, task_data: TaskUpdateDTO, user_id: str
    ) -> TaskResponseDTO:
        """
        Update a task.

        Args:
            project_id (str): Project ID
            task_id (str): Task ID
            task_data (TaskUpdateDTO): Task data
            user_id (str): User ID

        Returns:
            TaskResponseDTO: Updated task

        Raises:
            ProjectNotFoundException: If project not found
            TaskNotFoundException: If task not found
            NotProjectMemberException: If user is not a project member
            InsufficientProjectRoleException: If user has insufficient role
            InvalidTaskStatusTransitionException: If task status transition is invalid
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Get task
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )

        # Check if task exists
        if not task:
            raise TaskNotFoundException()

        # Check if user has sufficient role to update task
        is_task_creator = task.creator_id == user_id
        is_task_assignee = task.assignee_id == user_id
        is_project_admin = project_member.role in ["owner", "admin"]

        if not (is_task_creator or is_task_assignee or is_project_admin):
            raise InsufficientProjectRoleException(
                "Only task creator, assignee, or project admin can update the task"
            )

        # Check if status transition is valid
        if task_data.status is not None and task_data.status != task.status:
            # Implement status transition validation logic here
            # For example, you can't move from 'todo' to 'done' directly
            valid_transitions = {
                "todo": ["in_progress"],
                "in_progress": ["todo", "review"],
                "review": ["in_progress", "done"],
                "done": ["review"],
            }

            if task_data.status not in valid_transitions.get(task.status, []):
                raise InvalidTaskStatusTransitionException(
                    f"Cannot transition from '{task.status}' to '{task_data.status}'"
                )

        # Update task
        if task_data.title is not None:
            task.title = task_data.title

        if task_data.description is not None:
            task.description = task_data.description

        if task_data.assignee_id is not None:
            # Check if assignee is a project member
            if task_data.assignee_id:
                assignee_member = (
                    self.db.query(ProjectMember)
                    .filter(
                        ProjectMember.project_id == project_id,
                        ProjectMember.user_id == task_data.assignee_id,
                    )
                    .first()
                )

                if not assignee_member:
                    raise NotProjectMemberException("Assignee is not a project member")

            task.assignee_id = task_data.assignee_id

        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        if task_data.priority is not None:
            task.priority = task_data.priority

        if task_data.status is not None:
            command = ChangeTaskStatusCommand(self.db, task_id, task_data.status.value)
            task = command_invoker.execute_command(command)

        if task_data.tags is not None:
            task.tags = task_data.tags
        if task_data.meta_data is not None:
            task.meta_data = task_data.meta_data

        # Update task in database
        task.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(task)

        # Log activity
        self.activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="update_task",
            entity_type="task",
            entity_id=str(task.id),
            details=task_data.model_dump(exclude_none=True),
        )

        # Return task
        return self._task_to_dto(task)

    def delete_task(
        self, project_id: str, task_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Delete a task.

        Args:
            project_id (str): Project ID
            task_id (str): Task ID
            user_id (str): User ID

        Returns:
            Dict[str, Any]: Delete response

        Raises:
            ProjectNotFoundException: If project not found
            TaskNotFoundException: If task not found
            NotProjectMemberException: If user is not a project member
            InsufficientProjectRoleException: If user has insufficient role
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Get task
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )

        # Check if task exists
        if not task:
            raise TaskNotFoundException()

        # Check if user has sufficient role to delete task
        is_task_creator = task.creator_id == user_id
        is_project_admin = project_member.role in ["owner", "admin"]

        if not (is_task_creator or is_project_admin):
            raise InsufficientProjectRoleException(
                "Only task creator or project admin can delete the task"
            )

        # Log activity before deletion
        self.activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="delete_task",
            entity_type="task",
            entity_id=str(task.id),
            details=None,
        )

        # Delete task
        self.db.delete(task)
        self.db.commit()

        # Return success response
        return {"message": "Task deleted successfully"}

    def get_project_tasks(self, project_id: str, user_id: str) -> List[TaskResponseDTO]:
        """
        Get tasks for a project.

        Args:
            project_id (str): Project ID
            user_id (str): User ID

        Returns:
            List[TaskResponseDTO]: List of tasks

        Raises:
            ProjectNotFoundException: If project not found
            NotProjectMemberException: If user is not a project member
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Get tasks
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()

        # Return tasks
        return [self._task_to_dto(task) for task in tasks]

    def add_task_comment(
        self,
        project_id: str,
        task_id: str,
        comment_data: TaskCommentCreateDTO,
        user_id: str,
    ) -> TaskCommentResponseDTO:
        """
        Add a comment to a task.

        Args:
            project_id (str): Project ID
            task_id (str): Task ID
            comment_data (TaskCommentCreateDTO): Comment data
            user_id (str): User ID

        Returns:
            TaskCommentResponseDTO: Added comment

        Raises:
            ProjectNotFoundException: If project not found
            TaskNotFoundException: If task not found
            NotProjectMemberException: If user is not a project member
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Get task
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )

        # Check if task exists
        if not task:
            raise TaskNotFoundException()

        # Check if parent comment exists
        if comment_data.parent_id:
            parent_comment = (
                self.db.query(TaskComment)
                .filter(
                    TaskComment.id == comment_data.parent_id,
                    TaskComment.task_id == task_id,
                )
                .first()
            )

            if not parent_comment:
                raise TaskNotFoundException("Parent comment not found")

        # Create comment
        comment = TaskComment(
            task_id=task_id,
            user_id=user_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id,
        )

        # Add comment to database
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        # Log activity
        self.activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="add_comment",
            entity_type="task_comment",
            entity_id=str(comment.id),
            details=comment_data.model_dump(exclude_none=True),
        )

        # Return comment
        return self._task_comment_to_dto(comment)

    def get_task_comments(
        self, project_id: str, task_id: str, user_id: str
    ) -> List[TaskCommentResponseDTO]:
        """
        Get comments for a task.

        Args:
            project_id (str): Project ID
            task_id (str): Task ID
            user_id (str): User ID

        Returns:
            List[TaskCommentResponseDTO]: List of comments

        Raises:
            ProjectNotFoundException: If project not found
            TaskNotFoundException: If task not found
            NotProjectMemberException: If user is not a project member
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()

        # Check if project exists
        if not project:
            raise ProjectNotFoundException()

        # Check if user is a project member
        project_member = (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
            .first()
        )

        if not project_member:
            raise NotProjectMemberException()

        # Get task
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.project_id == project_id)
            .first()
        )

        # Check if task exists
        if not task:
            raise TaskNotFoundException()

        # Get comments
        comments = (
            self.db.query(TaskComment).filter(TaskComment.task_id == task_id).all()
        )

        # Return comments
        return [self._task_comment_to_dto(comment) for comment in comments]

    def _task_to_dto(self, task: Task) -> TaskResponseDTO:
        """
        Convert Task model to TaskResponseDTO.

        Args:
            task (Task): Task model

        Returns:
            TaskResponseDTO: Task DTO
        """
        return TaskResponseDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            creator_id=task.creator_id,
            assignee_id=task.assignee_id,
            due_date=task.due_date,
            priority=TaskPriority(task.priority),
            status=TaskStatus(task.status),
            tags=list(task.tags) if task.tags is not None else [],
            meta_data=dict(task.meta_data) if task.meta_data is not None else {},
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def _task_comment_to_dto(self, comment: TaskComment) -> TaskCommentResponseDTO:
        """
        Convert TaskComment model to TaskCommentResponseDTO.

        Args:
            comment (TaskComment): TaskComment model

        Returns:
            TaskCommentResponseDTO: TaskComment DTO
        """
        return TaskCommentResponseDTO(
            id=comment.id,
            task_id=comment.task_id,
            user_id=comment.user_id,
            content=comment.content,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
