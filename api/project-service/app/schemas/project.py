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


class ProjectMemberCreateDTO(BaseModel):
    """DTO for adding a member to a project"""
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
