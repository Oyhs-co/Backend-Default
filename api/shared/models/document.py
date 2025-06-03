from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Any, Optional

from .base import BaseModel


class Document(BaseModel):
    """Document model"""

    __tablename__ = "documents"

    name: Mapped[str] = mapped_column(String, nullable=False)
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id"), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("documents.id"), nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)  # 'file', 'folder', 'link'
    content_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # MIME type for files
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Size in bytes for files
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # For links or file URLs
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    creator_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    tags: Mapped[Optional[list[Any]]] = mapped_column(JSON, nullable=True)
    meta_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="documents")
    creator = relationship("User", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document")
    permissions = relationship("DocumentPermission", back_populates="document")
    children = relationship("Document", backref="parent", remote_side="Document.id")


class DocumentVersion(BaseModel):
    """Document version model"""

    __tablename__ = "document_versions"

    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    creator_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    changes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Description of changes

    # Relationships
    document = relationship("Document", back_populates="versions")


class DocumentPermission(BaseModel):
    """Document permission model"""

    __tablename__ = "document_permissions"

    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id"), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    role_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("roles.id"), nullable=True)
    can_view: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    can_edit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    can_share: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    document = relationship("Document", back_populates="permissions")
