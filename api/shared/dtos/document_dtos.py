from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Enum for document types"""
    FILE = "file"
    FOLDER = "folder"
    LINK = "link"


class DocumentCreateDTO(BaseModel):
    """DTO for creating a new document"""
    name: str = Field(..., min_length=1, max_length=255)
    project_id: str
    parent_id: Optional[str] = None  # For folder hierarchy
    type: DocumentType
    content_type: Optional[str] = None  # MIME type for files
    url: Optional[str] = None  # For links
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentUpdateDTO(BaseModel):
    """DTO for updating a document"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    parent_id: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponseDTO(BaseModel):
    """DTO for document response"""
    id: str
    name: str
    project_id: str
    parent_id: Optional[str] = None
    type: DocumentType
    content_type: Optional[str] = None
    size: Optional[int] = None  # Size in bytes for files
    url: Optional[str] = None
    description: Optional[str] = None
    version: int
    creator_id: str
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class DocumentVersionDTO(BaseModel):
    """DTO for document version"""
    id: str
    document_id: str
    version: int
    size: Optional[int] = None
    content_type: Optional[str] = None
    url: Optional[str] = None
    creator_id: str
    changes: Optional[str] = None
    created_at: datetime


class DocumentPermissionDTO(BaseModel):
    """DTO for document permissions"""
    id: str
    document_id: str
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    can_view: bool = True
    can_edit: bool = False
    can_delete: bool = False
    can_share: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None


class DocumentUploadResponseDTO(BaseModel):
    """DTO for document upload response"""
    document: DocumentResponseDTO
    upload_url: str  # Presigned URL for direct upload to storage