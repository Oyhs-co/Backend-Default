from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ExternalToolType(str, Enum):
    """Enum for external tool types"""
    GITHUB = "github"
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"
    ONEDRIVE = "onedrive"
    SLACK = "slack"
    JIRA = "jira"
    TRELLO = "trello"
    CUSTOM = "custom"


class OAuthProviderDTO(BaseModel):
    """DTO for OAuth provider information"""
    id: str
    name: str
    type: ExternalToolType
    auth_url: HttpUrl
    token_url: HttpUrl
    scope: str
    client_id: str
    redirect_uri: HttpUrl
    additional_params: Optional[Dict[str, Any]] = None


class OAuthRequestDTO(BaseModel):
    """DTO for OAuth request"""
    provider_id: str
    redirect_uri: Optional[HttpUrl] = None
    scope: Optional[str] = None
    state: Optional[str] = None


class OAuthCallbackDTO(BaseModel):
    """DTO for OAuth callback"""
    provider_id: str
    code: str
    state: Optional[str] = None
    error: Optional[str] = None


class ExternalToolConnectionDTO(BaseModel):
    """DTO for external tool connection"""
    id: str
    user_id: str
    provider_id: str
    provider_type: ExternalToolType
    account_name: Optional[str] = None
    account_email: Optional[str] = None
    account_id: Optional[str] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class ExternalToolConnectionCreateDTO(BaseModel):
    """DTO for creating an external tool connection"""
    provider_id: str
    access_token: str
    refresh_token: Optional[str] = None
    account_name: Optional[str] = None
    account_email: Optional[str] = None
    account_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class ExternalResourceDTO(BaseModel):
    """DTO for external resource"""
    id: str
    connection_id: str
    resource_id: str
    name: str
    type: str  # file, folder, repository, etc.
    url: Optional[HttpUrl] = None
    path: Optional[str] = None
    size: Optional[int] = None
    last_modified: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ExternalResourceSyncDTO(BaseModel):
    """DTO for external resource synchronization"""
    connection_id: str
    resource_id: str
    project_id: Optional[str] = None
    target_folder_id: Optional[str] = None
    sync_direction: str = "download"  # download, upload, bidirectional
    auto_sync: bool = False
    sync_interval: Optional[int] = None  # in minutes