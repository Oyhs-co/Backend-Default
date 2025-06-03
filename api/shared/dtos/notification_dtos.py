from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class NotificationType(str, Enum):
    """Enum for notification types"""

    SYSTEM = "system"
    PROJECT = "project"
    TASK = "task"
    DOCUMENT = "document"
    MENTION = "mention"
    INVITATION = "invitation"
    REMINDER = "reminder"


class NotificationPriority(str, Enum):
    """Enum for notification priority"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class NotificationChannel(str, Enum):
    """Enum for notification channels"""

    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class NotificationCreateDTO(BaseModel):
    """DTO for creating a notification"""

    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    action_url: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None  # For scheduled notifications


class NotificationResponseDTO(BaseModel):
    """DTO for notification response"""

    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    action_url: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


class NotificationUpdateDTO(BaseModel):
    """DTO for updating a notification"""

    is_read: Optional[bool] = None


class NotificationBatchCreateDTO(BaseModel):
    """DTO for creating multiple notifications at once"""

    user_ids: List[str]
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    action_url: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None


class NotificationPreferencesDTO(BaseModel):
    """DTO for user notification preferences"""

    user_id: str
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = False
    in_app_enabled: bool = True
    digest_enabled: bool = False
    digest_frequency: Optional[str] = None  # daily, weekly
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None  # HH:MM format
    preferences_by_type: Optional[Dict[str, Dict[str, bool]]] = (
        None  # Type -> Channel -> Enabled
    )
