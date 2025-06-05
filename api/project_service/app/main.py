from typing import Any, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Path, Query, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.project_service.app.commands.task_commands import (
    AssignTaskCommand,
    ChangeTaskStatusCommand,
    CommandInvoker,
)
from api.shared.middleware.auth_middleware import auth_middleware
from api.project_service.app.schemas.activity import ActivityLogResponseDTO
from api.project_service.app.schemas.project import (
    ProjectCreateDTO,
    ProjectMemberCreateDTO,
    ProjectMemberResponseDTO,
    ProjectMemberUpdateDTO,
    ProjectResponseDTO,
    ProjectUpdateDTO,
)
from api.project_service.app.schemas.task import (
    TaskCommentCreateDTO,
    TaskCommentResponseDTO,
    TaskCreateDTO,
    TaskResponseDTO,
    TaskUpdateDTO,
)
from api.project_service.app.services.activity_service import ActivityService
from api.project_service.app.services.project_service import ProjectService
from api.project_service.app.services.task_service import TaskService
from api.shared.exceptions.auth_exceptions import InvalidTokenException
from api.shared.utils.db import get_db
from api.shared.utils.jwt import decode_token

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TaskHub Project Service",
    description="Project management service for TaskHub platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Create command invoker
command_invoker = CommandInvoker()


def get_current_user(token: str = Security(oauth2_scheme)) -> str:
    """
    Get current user ID from token.

    Args:
        token (str): JWT token

    Returns:
        str: User ID

    Raises:
        InvalidTokenException: If token is invalid
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenException()

        return user_id
    except Exception:
        raise InvalidTokenException()


# Project endpoints
@app.post("/projects", response_model=ProjectResponseDTO, tags=["Projects"])
async def create_project(
    project_data: ProjectCreateDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Create a new project.

    Args:
        project_data (ProjectCreateDTO): Project data
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ProjectResponseDTO: Created project
    """
    project_service = ProjectService(db)
    return project_service.create_project(project_data, user_id)


@app.get("/projects", response_model=List[ProjectResponseDTO], tags=["Projects"])
async def get_user_projects(
    db: Session = Depends(get_db), user_id: str = Depends(get_current_user)
):
    """
    Get projects for current user.

    Args:
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[ProjectResponseDTO]: List of projects
    """
    project_service = ProjectService(db)
    return project_service.get_user_projects(user_id)


@app.get("/projects/{project_id}", response_model=ProjectResponseDTO, tags=["Projects"])
async def get_project(
    project_id: str = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get a project.

    Args:
        project_id (str): Project ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ProjectResponseDTO: Project
    """
    project_service = ProjectService(db)
    return project_service.get_project(project_id, user_id)


@app.put("/projects/{project_id}", response_model=ProjectResponseDTO, tags=["Projects"])
async def update_project(
    project_data: ProjectUpdateDTO,
    project_id: str = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Update a project.

    Args:
        project_data (ProjectUpdateDTO): Project data
        project_id (str): Project ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ProjectResponseDTO: Updated project
    """
    project_service = ProjectService(db)
    return project_service.update_project(project_id, project_data, user_id)


@app.delete("/projects/{project_id}", tags=["Projects"])
async def delete_project(
    project_id: str = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Delete a project.

    Args:
        project_id (str): Project ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Dict[str, Any]: Delete response
    """
    project_service = ProjectService(db)
    return project_service.delete_project(project_id, user_id)


# Project members endpoints
@app.post(
    "/projects/{project_id}/members",
    response_model=ProjectMemberResponseDTO,
    tags=["Project Members"],
)
async def add_project_member(
    member_data: ProjectMemberCreateDTO,
    project_id: str = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Add a member to a project.

    Args:
        member_data (ProjectMemberCreateDTO): Member data
        project_id (str): Project ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ProjectMemberResponseDTO: Added project member
    """
    project_service = ProjectService(db)
    return project_service.add_project_member(project_id, member_data, user_id)


@app.get(
    "/projects/{project_id}/members",
    response_model=List[ProjectMemberResponseDTO],
    tags=["Project Members"],
)
async def get_project_members(
    project_id: str = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get project members.

    Args:
        project_id (str): Project ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[ProjectMemberResponseDTO]: List of project members
    """
    project_service = ProjectService(db)
    return project_service.get_project_members(project_id, user_id)


@app.put(
    "/projects/{project_id}/members/{member_id}",
    response_model=ProjectMemberResponseDTO,
    tags=["Project Members"],
)
async def update_project_member(
    member_data: ProjectMemberUpdateDTO,
    project_id: str = Path(..., description="Project ID"),
    member_id: str = Path(..., description="Member ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Update a project member.

    Args:
        member_data (ProjectMemberUpdateDTO): Member data
        project_id (str): Project ID
        member_id (str): Member ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        ProjectMemberResponseDTO: Updated project member
    """
    project_service = ProjectService(db)
    return project_service.update_project_member(
        project_id, member_id, member_data, user_id
    )


@app.delete("/projects/{project_id}/members/{member_id}", tags=["Project Members"])
async def remove_project_member(
    project_id: str = Path(..., description="Project ID"),
    member_id: str = Path(..., description="Member ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Remove a project member.

    Args:
        project_id (str): Project ID
        member_id (str): Member ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Dict[str, Any]: Remove response
    """
    project_service = ProjectService(db)
    return project_service.remove_project_member(project_id, member_id, user_id)


# Task endpoints
@app.post(
    "/projects/{project_id}/tasks", response_model=TaskResponseDTO, tags=["Tasks"]
)
async def create_task(
    task_data: TaskCreateDTO,
    project_id: str = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Create a new task.

    Args:
        task_data (TaskCreateDTO): Task data
        project_id (str): Project ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        TaskResponseDTO: Created task
    """
    task_service = TaskService(db)
    return task_service.create_task(project_id, task_data, user_id)


@app.get(
    "/projects/{project_id}/tasks", response_model=List[TaskResponseDTO], tags=["Tasks"]
)
async def get_project_tasks(
    project_id: str = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get tasks for a project.

    Args:
        project_id (str): Project ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[TaskResponseDTO]: List of tasks
    """
    task_service = TaskService(db)
    return task_service.get_project_tasks(project_id, user_id)


@app.get(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=TaskResponseDTO,
    tags=["Tasks"],
)
async def get_task(
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get a task.

    Args:
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        TaskResponseDTO: Task
    """
    task_service = TaskService(db)
    return task_service.get_task(project_id, task_id, user_id)


@app.put(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=TaskResponseDTO,
    tags=["Tasks"],
)
async def update_task(
    task_data: TaskUpdateDTO,
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Update a task.

    Args:
        task_data (TaskUpdateDTO): Task data
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        TaskResponseDTO: Updated task
    """
    task_service = TaskService(db)
    return task_service.update_task(project_id, task_id, task_data, user_id)


@app.delete("/projects/{project_id}/tasks/{task_id}", tags=["Tasks"])
async def delete_task(
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Delete a task.

    Args:
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        Dict[str, Any]: Delete response
    """
    task_service = TaskService(db)
    return task_service.delete_task(project_id, task_id, user_id)


# Task comments endpoints
@app.post(
    "/projects/{project_id}/tasks/{task_id}/comments",
    response_model=TaskCommentResponseDTO,
    tags=["Task Comments"],
)
async def add_task_comment(
    comment_data: TaskCommentCreateDTO,
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Add a comment to a task.

    Args:
        comment_data (TaskCommentCreateDTO): Comment data
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        TaskCommentResponseDTO: Added comment
    """
    task_service = TaskService(db)
    return task_service.add_task_comment(project_id, task_id, comment_data, user_id)


@app.get(
    "/projects/{project_id}/tasks/{task_id}/comments",
    response_model=List[TaskCommentResponseDTO],
    tags=["Task Comments"],
)
async def get_task_comments(
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get comments for a task.

    Args:
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[TaskCommentResponseDTO]: List of comments
    """
    task_service = TaskService(db)
    return task_service.get_task_comments(project_id, task_id, user_id)


# Activity endpoints
@app.get(
    "/projects/{project_id}/activities",
    response_model=List[ActivityLogResponseDTO],
    tags=["Activities"],
)
async def get_project_activities(
    project_id: str = Path(..., description="Project ID"),
    limit: int = Query(100, description="Limit"),
    offset: int = Query(0, description="Offset"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get activities for a project.

    Args:
        project_id (str): Project ID
        limit (int): Limit
        offset (int): Offset
        db (Session): Database session
        user_id (str): User ID

    Returns:
        List[ActivityLogResponseDTO]: List of activities
    """
    # Check if user is a project member
    project_service = ProjectService(db)
    project_service.get_project(
        project_id, user_id
    )  # This will raise an exception if user is not a project member

    activity_service = ActivityService(db)
    return activity_service.get_project_activities(project_id, limit, offset)


# Command pattern endpoints
@app.post(
    "/projects/{project_id}/tasks/{task_id}/assign",
    response_model=TaskResponseDTO,
    tags=["Task Commands"],
)
async def assign_task(
    assignee_id: Optional[str] = Query(None, description="Assignee ID"),
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Assign a task to a user.

    Args:
        assignee_id (Optional[str]): Assignee ID
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        TaskResponseDTO: Updated task
    """
    # Check if user is a project member
    project_service = ProjectService(db)
    project_service.get_project(
        project_id, user_id
    )  # This will raise an exception if user is not a project member

    # Create command
    command = AssignTaskCommand(db, task_id, assignee_id)

    # Execute command
    task = command_invoker.execute_command(command)

    # Log activity
    activity_service = ActivityService(db)
    activity_service.log_activity(
        project_id=project_id,
        user_id=user_id,
        action="assign",
        entity_type="task",
        entity_id=task_id,
        details={"assignee_id": assignee_id},
    )

    # Return task
    return TaskResponseDTO(
        id=task.id,
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        creator_id=task.creator_id,
        assignee_id=task.assignee_id,
        due_date=task.due_date,
        priority=task.priority,
        status=task.status,
        tags=list(task.tags) if task.tags is not None else [],
        metadata=(task.metadata or {}),
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@app.post(
    "/projects/{project_id}/tasks/{task_id}/status",
    response_model=TaskResponseDTO,
    tags=["Task Commands"],
)
async def change_task_status(
    status: str = Query(..., description="Task status"),
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Change task status.

    Args:
        status (str): Task status
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        TaskResponseDTO: Updated task
    """
    # Check if user is a project member
    project_service = ProjectService(db)
    project_service.get_project(
        project_id, user_id
    )  # This will raise an exception if user is not a project member

    # Create command
    command = ChangeTaskStatusCommand(db, task_id, status)

    # Execute command
    task = command_invoker.execute_command(command)

    # Log activity
    activity_service = ActivityService(db)
    activity_service.log_activity(
        project_id=project_id,
        user_id=user_id,
        action="change_status",
        entity_type="task",
        entity_id=task_id,
        details={"status": status},
    )

    # Return task
    return TaskResponseDTO(
        id=task.id,
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        creator_id=task.creator_id,
        assignee_id=task.assignee_id,
        due_date=task.due_date,
        priority=task.priority,
        status=task.status,
        tags=list(task.tags) if task.tags is not None else [],
        metadata=(task.metadata or {}),
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@app.post(
    "/projects/{project_id}/tasks/{task_id}/undo",
    response_model=TaskResponseDTO,
    tags=["Task Commands"],
)
async def undo_task_command(
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Undo the last task command.

    Args:
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        TaskResponseDTO: Updated task
    """
    # Check if user is a project member
    project_service = ProjectService(db)
    project_service.get_project(
        project_id, user_id
    )  # This will raise an exception if user is not a project member

    try:
        # Undo command
        task = command_invoker.undo()

        # Log activity
        activity_service = ActivityService(db)
        activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="undo",
            entity_type="task",
            entity_id=task_id,
            details=None,
        )

        # Return task
        return TaskResponseDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            creator_id=task.creator_id,
            assignee_id=task.assignee_id,
            due_date=task.due_date,
            priority=task.priority,
            status=task.status,
            tags=list(task.tags) if task.tags is not None else [],
            metadata=(task.metadata or {}),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/projects/{project_id}/tasks/{task_id}/redo",
    response_model=TaskResponseDTO,
    tags=["Task Commands"],
)
async def redo_task_command(
    project_id: str = Path(..., description="Project ID"),
    task_id: str = Path(..., description="Task ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Redo the last undone task command.

    Args:
        project_id (str): Project ID
        task_id (str): Task ID
        db (Session): Database session
        user_id (str): User ID

    Returns:
        TaskResponseDTO: Updated task
    """
    # Check if user is a project member
    project_service = ProjectService(db)
    project_service.get_project(
        project_id, user_id
    )  # This will raise an exception if user is not a project member

    try:
        # Redo command
        task = command_invoker.redo()

        # Log activity
        activity_service = ActivityService(db)
        activity_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            action="redo",
            entity_type="task",
            entity_id=task_id,
            details=None,
        )

        # Return task
        return TaskResponseDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            creator_id=task.creator_id,
            assignee_id=task.assignee_id,
            due_date=task.due_date,
            priority=task.priority,
            status=task.status,
            tags=list(task.tags) if task.tags is not None else [],
            metadata=(task.metadata or {}),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health", tags=["Health"])
async def health_check() -> Any:
    """
    Health check endpoint.

    Returns:
        Dict[str, str]: Health status
    """
    return {"status": "healthy"}

# Export para tests de integración
get_db = get_db
get_current_user = get_current_user
auth_middleware = auth_middleware
