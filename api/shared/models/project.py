from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class Project(BaseModel):
    """Project model"""

    __tablename__ = "projects"

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="planning")
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    tags = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)

    # Relationships
    members = relationship("ProjectMember", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    documents = relationship("Document", back_populates="project")
    activity_logs = relationship("ActivityLog", back_populates="project")


class ProjectMember(BaseModel):
    """Project member model"""

    __tablename__ = "project_members"

    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(
        String, nullable=False, default="member"
    )  # 'owner', 'admin', 'member'
    joined_at = Column(DateTime, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="projects")


class Task(BaseModel):
    """Task model"""

    __tablename__ = "tasks"

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(
        String, nullable=False, default="medium"
    )  # 'low', 'medium', 'high', 'urgent'
    status = Column(
        String, nullable=False, default="todo"
    )  # 'todo', 'in_progress', 'review', 'done'
    tags = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    creator = relationship(
        "User", foreign_keys=[creator_id], back_populates="tasks_created"
    )
    assignee = relationship(
        "User", foreign_keys=[assignee_id], back_populates="tasks_assigned"
    )
    comments = relationship("TaskComment", back_populates="task")


class TaskComment(BaseModel):
    """Task comment model"""

    __tablename__ = "task_comments"

    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(String, ForeignKey("task_comments.id"), nullable=True)

    # Relationships
    task = relationship("Task", back_populates="comments")
    parent = relationship(
        "TaskComment", remote_side="TaskComment.id", backref="replies"
    )


class ActivityLog(BaseModel):
    """Activity log model"""

    __tablename__ = "activity_logs"

    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # 'project', 'task', 'document', etc.
    entity_id = Column(String, nullable=False)
    details = Column(JSON, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="activity_logs")
    user = relationship("User", back_populates="activity_logs")
