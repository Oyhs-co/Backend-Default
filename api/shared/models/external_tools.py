from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel


class OAuthProvider(BaseModel):
    """OAuth provider model"""
    __tablename__ = 'oauth_providers'

    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'github', 'google_drive', 'dropbox', etc.
    auth_url = Column(String, nullable=False)
    token_url = Column(String, nullable=False)
    scope = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False)
    additional_params = Column(JSON, nullable=True)

    # Relationships
    connections = relationship("ExternalToolConnection", back_populates="provider")


class ExternalToolConnection(BaseModel):
    """External tool connection model"""
    __tablename__ = 'external_tool_connections'

    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    provider_id = Column(String, ForeignKey('oauth_providers.id'), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_type = Column(String, nullable=True)
    scope = Column(String, nullable=True)
    account_name = Column(String, nullable=True)
    account_email = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    metadata = Column(JSON, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="external_connections")
    provider = relationship("OAuthProvider", back_populates="connections")
    resources = relationship("ExternalResource", back_populates="connection")


class ExternalResource(BaseModel):
    """External resource model"""
    __tablename__ = 'external_resources'

    connection_id = Column(String, ForeignKey('external_tool_connections.id'), nullable=False)
    resource_id = Column(String, nullable=False)  # ID in the external system
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'file', 'folder', 'repository', etc.
    url = Column(String, nullable=True)
    path = Column(String, nullable=True)
    size = Column(String, nullable=True)
    last_modified = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    sync_enabled = Column(Boolean, nullable=False, default=False)
    sync_direction = Column(String, nullable=True)  # 'download', 'upload', 'bidirectional'
    sync_interval = Column(Integer, nullable=True)  # in minutes
    last_synced_at = Column(DateTime, nullable=True)
    project_id = Column(String, ForeignKey('projects.id'), nullable=True)
    document_id = Column(String, ForeignKey('documents.id'), nullable=True)

    # Relationships
    connection = relationship("ExternalToolConnection", back_populates="resources")