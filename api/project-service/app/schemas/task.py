from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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


class TaskCreateDTO(BaseModel):
    """DTO for creating a new task"""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
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


class TaskCommentCreateDTO(BaseModel):
    """DTO for creating a task comment"""
    content: str = Field(..., min_length=1)
    parent_id: Optional[str] = None


class TaskCommentResponseDTO(BaseModel):
    """DTO for task comment response"""
    id: str
    task_id: str
    user_id: str
    content: str
    parent_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
