from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Document(BaseModel):
    """Document model"""
    __tablename__ = 'documents'

    name = Column(String, nullable=False)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    parent_id = Column(String, ForeignKey('documents.id'), nullable=True)  # For folder hierarchy
    type = Column(String, nullable=False)  # 'file', 'folder', 'link'
    content_type = Column(String, nullable=True)  # MIME type for files
    size = Column(Integer, nullable=True)  # Size in bytes for files
    url = Column(String, nullable=True)  # For links or file URLs
    description = Column(Text, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    creator_id = Column(String, ForeignKey('users.id'), nullable=False)
    tags = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="documents")
    creator = relationship("User", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document")
    permissions = relationship("DocumentPermission", back_populates="document")
    children = relationship("Document", backref="parent", remote_side="Document.id")


class DocumentVersion(BaseModel):
    """Document version model"""
    __tablename__ = 'document_versions'

    document_id = Column(String, ForeignKey('documents.id'), nullable=False)
    version = Column(Integer, nullable=False)
    size = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    url = Column(String, nullable=True)
    creator_id = Column(String, ForeignKey('users.id'), nullable=False)
    changes = Column(Text, nullable=True)  # Description of changes

    # Relationships
    document = relationship("Document", back_populates="versions")


class DocumentPermission(BaseModel):
    """Document permission model"""
    __tablename__ = 'document_permissions'

    document_id = Column(String, ForeignKey('documents.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=True)
    role_id = Column(String, ForeignKey('roles.id'), nullable=True)
    can_view = Column(Boolean, nullable=False, default=True)
    can_edit = Column(Boolean, nullable=False, default=False)
    can_delete = Column(Boolean, nullable=False, default=False)
    can_share = Column(Boolean, nullable=False, default=False)

    # Relationships
    document = relationship("Document", back_populates="permissions")