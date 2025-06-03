import pytest
from api.shared.dtos.notification_dtos import (
    NotificationType, NotificationPriority, NotificationChannel,
    NotificationCreateDTO, NotificationResponseDTO, NotificationUpdateDTO,
    NotificationBatchCreateDTO, NotificationPreferencesDTO
)
from datetime import datetime

def test_notification_type_enum():
    assert NotificationType.SYSTEM.value == 'system'
    assert NotificationType.REMINDER.value == 'reminder'

def test_notification_priority_enum():
    assert NotificationPriority.LOW.value == 'low'
    assert NotificationPriority.HIGH.value == 'high'

def test_notification_channel_enum():
    assert NotificationChannel.IN_APP.value == 'in_app'
    assert NotificationChannel.SMS.value == 'sms'

def test_notification_create_dto():
    dto = NotificationCreateDTO(
        user_id='uid', type=NotificationType.SYSTEM, title='T', message='M'
    )
    assert dto.user_id == 'uid'
    assert dto.type == NotificationType.SYSTEM
    assert dto.priority == NotificationPriority.NORMAL
    assert NotificationChannel.IN_APP in dto.channels

def test_notification_response_dto():
    now = datetime.now()
    dto = NotificationResponseDTO(
        id='id', user_id='uid', type=NotificationType.TASK, title='T', message='M',
        priority=NotificationPriority.HIGH, channels=[NotificationChannel.PUSH], created_at=now
    )
    assert dto.id == 'id'
    assert dto.type == NotificationType.TASK
    assert NotificationChannel.PUSH in dto.channels
    assert dto.created_at == now
    assert dto.is_read is False

def test_notification_update_dto():
    dto = NotificationUpdateDTO(is_read=True)
    assert dto.is_read is True

def test_notification_batch_create_dto():
    dto = NotificationBatchCreateDTO(
        user_ids=['u1', 'u2'], type=NotificationType.DOCUMENT, title='T', message='M'
    )
    assert 'u1' in dto.user_ids
    assert dto.type == NotificationType.DOCUMENT
    assert dto.priority == NotificationPriority.NORMAL

def test_notification_preferences_dto():
    dto = NotificationPreferencesDTO(user_id='uid')
    assert dto.user_id == 'uid'
    assert dto.email_enabled is True
    assert dto.push_enabled is True
    assert dto.sms_enabled is False
    assert dto.in_app_enabled is True
    assert dto.digest_enabled is False 