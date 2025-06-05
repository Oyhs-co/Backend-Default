import pytest
from unittest.mock import patch, MagicMock
from api.notification_service.app.observers.notification_observer import (
    EmailNotificationObserver, PushNotificationObserver, SMSNotificationObserver
)
from api.notification_service.app.schemas.notification import NotificationChannel
from api.shared.models.notification import Notification
from typing import List

def make_notification(channels: List[NotificationChannel]) -> Notification:
    notif = MagicMock(spec=Notification)
    notif.user_id = 'user1'
    notif.title = 'Test'
    notif.message = 'Msg'
    notif.action_url = None
    notif.channels = channels
    notif.id = 'nid'
    notif.type = 'system'
    notif.related_entity_type = None
    notif.related_entity_id = None
    return notif

@pytest.fixture
def notification() -> Notification:
    return make_notification([NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.SMS])

def test_email_notify_enabled(notification: Notification) -> None:
    observer = EmailNotificationObserver()
    with patch('api.external_tools_service.app.services.email_tools.send_email_brevo') as mock_brevo, \
         patch.object(observer, '_get_user_email', return_value='test@example.com'):
        observer.notify(notification)
        mock_brevo.assert_called()

def test_email_notify_disabled() -> None:
    observer = EmailNotificationObserver()
    notif = make_notification([NotificationChannel.PUSH])
    with patch('api.external_tools_service.app.services.email_tools.send_email_brevo') as mock_brevo:
        observer.notify(notif)
        mock_brevo.assert_not_called()

def test_push_notify_enabled(notification: Notification) -> None:
    observer = PushNotificationObserver()
    with patch.object(observer, '_get_user_device_tokens', return_value=['token1']), \
         patch('requests.post') as mock_post:
        observer.notify(notification)
        mock_post.assert_called()

def test_push_notify_disabled() -> None:
    observer = PushNotificationObserver()
    notif = make_notification([NotificationChannel.EMAIL])
    with patch('requests.post') as mock_post:
        observer.notify(notif)
        mock_post.assert_not_called()

def test_sms_notify_enabled(notification: Notification) -> None:
    observer = SMSNotificationObserver()
    with patch.object(observer, '_get_user_phone_number', return_value='+1234567890'), \
         patch('requests.post') as mock_post:
        observer.notify(notification)
        mock_post.assert_called()

def test_sms_notify_disabled() -> None:
    observer = SMSNotificationObserver()
    notif = make_notification([NotificationChannel.EMAIL])
    with patch('requests.post') as mock_post:
        observer.notify(notif)
        mock_post.assert_not_called() 