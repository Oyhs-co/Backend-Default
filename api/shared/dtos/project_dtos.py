from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """Enum for project status"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Enum for task priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Enum for task status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class ProjectCreateDTO(BaseModel):
    """DTO for creating a new project"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectUpdateDTO(BaseModel):
    """DTO for updating a project"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectResponseDTO(BaseModel):
    """DTO for project response"""
    id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ProjectStatus
    owner_id: str
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class TaskCreateDTO(BaseModel):
    """DTO for creating a new task"""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    project_id: str
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskUpdateDTO(BaseModel):
    """DTO for updating a task"""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResponseDTO(BaseModel):
    """DTO for task response"""
    id: str
    title: str
    description: Optional[str] = None
    project_id: str
    creator_id: str
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority
    status: TaskStatus
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProjectMemberCreateDTO(BaseModel):
    """DTO for adding a member to a project"""
    project_id: str
    user_id: str
    role: str = "member"  # Default role is member


class ProjectMemberUpdateDTO(BaseModel):
    """DTO for updating a project member"""
    role: str


class ProjectMemberResponseDTO(BaseModel):
    """DTO for project member response"""
    id: str
    project_id: str
    user_id: str
    role: str
    joined_at: datetime


class ActivityLogDTO(BaseModel):
    """DTO for activity log"""
    id: str
    project_id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime