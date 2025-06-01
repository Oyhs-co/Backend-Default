from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel


class Notification(BaseModel):
    """Notification model"""
    __tablename__ = 'notifications'

    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False)  # 'system', 'project', 'task', 'document', etc.
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String, nullable=False, default='normal')  # 'low', 'normal', 'high'
    channels = Column(JSON, nullable=False)  # ['in_app', 'email', 'push', 'sms']
    related_entity_type = Column(String, nullable=True)  # 'project', 'task', 'document', etc.
    related_entity_id = Column(String, nullable=True)
    action_url = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)  # For scheduled notifications
    sent_at = Column(DateTime, nullable=True)  # When the notification was actually sent

    # Relationships
    user = relationship("User", back_populates="notifications")


class NotificationPreference(BaseModel):
    """Notification preference model"""
    __tablename__ = 'notification_preferences'

    user_id = Column(String, ForeignKey('users.id'), nullable=False, unique=True)
    email_enabled = Column(Boolean, nullable=False, default=True)
    push_enabled = Column(Boolean, nullable=False, default=True)
    sms_enabled = Column(Boolean, nullable=False, default=False)
    in_app_enabled = Column(Boolean, nullable=False, default=True)
    digest_enabled = Column(Boolean, nullable=False, default=False)
    digest_frequency = Column(String, nullable=True)  # 'daily', 'weekly'
    quiet_hours_enabled = Column(Boolean, nullable=False, default=False)
    quiet_hours_start = Column(String, nullable=True)  # HH:MM format
    quiet_hours_end = Column(String, nullable=True)  # HH:MM format
    preferences_by_type = Column(JSON, nullable=True)  # Type -> Channel -> Enabled