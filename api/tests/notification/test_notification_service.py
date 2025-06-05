import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from api.notification_service.app.services.notification_service import NotificationService
from api.notification_service.app.schemas.notification import NotificationCreateDTO, NotificationBatchCreateDTO, NotificationType, NotificationResponseDTO, NotificationPriority

@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()

@pytest.fixture
def notification_service(mock_db: MagicMock) -> NotificationService:
    return NotificationService(mock_db)

def test_create_notification_success(notification_service: NotificationService):
    notif_data = NotificationCreateDTO(user_id="user1", type=NotificationType.SYSTEM, title="Test", message="Msg")
    mock_response = NotificationResponseDTO(
        id="notif1", user_id="user1", type=NotificationType.SYSTEM, title="Test", message="Msg", priority=NotificationPriority.NORMAL, channels=[], created_at=datetime.now()
    )
    with patch("api.shared.models.notification.Notification", MagicMock()), \
         patch.object(notification_service.db, "add"), \
         patch.object(notification_service.db, "commit"), \
         patch.object(notification_service, "_notification_to_dto", return_value=mock_response), \
         patch.object(notification_service, "_get_or_create_preferences") as mock_prefs:
        # Mock preferences con quiet_hours_start y quiet_hours_end como None
        mock_pref = MagicMock()
        mock_pref.email_enabled = True
        mock_pref.push_enabled = True
        mock_pref.sms_enabled = True
        mock_pref.in_app_enabled = True
        mock_pref.preferences_by_type = None
        mock_pref.quiet_hours_enabled = False
        mock_pref.quiet_hours_start = None
        mock_pref.quiet_hours_end = None
        mock_prefs.return_value = mock_pref
        result = notification_service.create_notification(notif_data)
        assert result.id == "notif1"

def test_create_batch_notifications(notification_service: NotificationService):
    batch_data = NotificationBatchCreateDTO(user_ids=["user1", "user2"], type=NotificationType.SYSTEM, title="Test", message="Msg")
    mock_response = NotificationResponseDTO(
        id="notif1", user_id="user1", type=NotificationType.SYSTEM, title="Test", message="Msg", priority=NotificationPriority.NORMAL, channels=[], created_at=datetime.now()
    )
    with patch("api.shared.models.notification.Notification", MagicMock()), \
         patch.object(notification_service.db, "add"), \
         patch.object(notification_service.db, "commit"), \
         patch.object(notification_service, "_notification_to_dto", return_value=mock_response), \
         patch.object(notification_service, "_get_or_create_preferences") as mock_prefs:
        mock_pref = MagicMock()
        mock_pref.email_enabled = True
        mock_pref.push_enabled = True
        mock_pref.sms_enabled = True
        mock_pref.in_app_enabled = True
        mock_pref.preferences_by_type = None
        mock_pref.quiet_hours_enabled = False
        mock_pref.quiet_hours_start = None
        mock_pref.quiet_hours_end = None
        mock_prefs.return_value = mock_pref
        result = notification_service.create_batch_notifications(batch_data)
        assert isinstance(result, list)
        assert result[0].id == "notif1"

def test_get_user_notifications(notification_service: NotificationService):
    mock_response = NotificationResponseDTO(
        id="notif1", user_id="user1", type=NotificationType.SYSTEM, title="Test", message="Msg", priority=NotificationPriority.NORMAL, channels=[], created_at=datetime.now()
    )
    with patch("api.shared.models.notification.Notification", MagicMock()), \
         patch("api.shared.models.notification.NotificationPreference", MagicMock()), \
         patch.object(notification_service.db, "query") as mock_query, \
         patch.object(notification_service, "_notification_to_dto", return_value=mock_response):
        mock_chain = MagicMock()
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value = mock_chain
        mock_chain.offset.return_value = mock_chain
        mock_chain.limit.return_value = mock_chain
        mock_chain.all.return_value = [MagicMock()]
        mock_query.return_value = mock_chain
        result = notification_service.get_user_notifications("user1", 10, 0)
        assert isinstance(result, list)
        assert result[0].id == "notif1"

def test_get_unread_notifications(notification_service: NotificationService):
    mock_response = NotificationResponseDTO(
        id="notif1", user_id="user1", type=NotificationType.SYSTEM, title="Test", message="Msg", priority=NotificationPriority.NORMAL, channels=[], created_at=datetime.now()
    )
    with patch("api.shared.models.notification.Notification", MagicMock()), \
         patch.object(notification_service.db, "query") as mock_query, \
         patch.object(notification_service, "_notification_to_dto", return_value=mock_response):
        mock_chain = MagicMock()
        mock_chain.filter.return_value = mock_chain
        mock_chain.order_by.return_value = mock_chain
        mock_chain.offset.return_value = mock_chain
        mock_chain.limit.return_value = mock_chain
        mock_chain.all.return_value = [MagicMock()]
        mock_query.return_value = mock_chain
        result = notification_service.get_unread_notifications("user1", 10, 0)
        assert isinstance(result, list)
        assert result[0].id == "notif1"

def test_mark_notification_as_read(notification_service: NotificationService):
    mock_response = NotificationResponseDTO(
        id="notif1", user_id="user1", type=NotificationType.SYSTEM, title="Test", message="Msg", priority=NotificationPriority.NORMAL, channels=[], created_at=datetime.now()
    )
    with patch("api.shared.models.notification.Notification", MagicMock()), \
         patch.object(notification_service.db, "query") as mock_query, \
         patch.object(notification_service, "_notification_to_dto", return_value=mock_response), \
         patch.object(notification_service.db, "commit"), \
         patch.object(notification_service.db, "refresh"):
        mock_chain = MagicMock()
        mock_chain.filter.return_value = mock_chain
        mock_chain.first.return_value = MagicMock()
        mock_query.return_value = mock_chain
        result = notification_service.mark_notification_as_read("notif1", "user1")
        assert result.id == "notif1"

def test_mark_all_notifications_as_read(notification_service: NotificationService):
    with patch.object(notification_service.db, "query") as mock_query, \
         patch.object(notification_service.db, "commit"):
        mock_chain = MagicMock()
        mock_chain.filter.return_value = mock_chain
        mock_chain.update.return_value = None
        mock_query.return_value = mock_chain
        result = notification_service.mark_all_notifications_as_read("user1")
        assert "message" in result

def test_delete_notification(notification_service: NotificationService):
    with patch("api.shared.models.notification.Notification", MagicMock()), \
         patch.object(notification_service.db, "query") as mock_query, \
         patch.object(notification_service.db, "delete"), \
         patch.object(notification_service.db, "commit"):
        mock_chain = MagicMock()
        mock_chain.filter.return_value = mock_chain
        mock_chain.first.return_value = MagicMock()
        mock_query.return_value = mock_chain
        result = notification_service.delete_notification("notif1", "user1")
        assert "message" in result

def test_get_notification_preferences(notification_service: NotificationService):
    mock_pref = MagicMock()
    mock_pref.user_id = "user1"
    mock_pref.email_enabled = True
    mock_pref.push_enabled = True
    mock_pref.sms_enabled = False
    mock_pref.in_app_enabled = True
    mock_pref.digest_enabled = False
    mock_pref.digest_frequency = None
    mock_pref.quiet_hours_enabled = False
    mock_pref.quiet_hours_start = None
    mock_pref.quiet_hours_end = None
    mock_pref.preferences_by_type = None
    with patch.object(notification_service, "_get_or_create_preferences", return_value=mock_pref):
        result = notification_service.get_notification_preferences("user1")
        assert result.user_id == "user1"

def test_update_notification_preferences(notification_service: NotificationService):
    mock_pref = MagicMock()
    mock_pref.user_id = "user1"
    mock_pref.email_enabled = True
    mock_pref.push_enabled = True
    mock_pref.sms_enabled = False
    mock_pref.in_app_enabled = True
    mock_pref.digest_enabled = False
    mock_pref.digest_frequency = None
    mock_pref.quiet_hours_enabled = False
    mock_pref.quiet_hours_start = None
    mock_pref.quiet_hours_end = None
    mock_pref.preferences_by_type = None
    with patch.object(notification_service, "_get_or_create_preferences", return_value=mock_pref), \
         patch.object(notification_service.db, "commit"), \
         patch.object(notification_service.db, "refresh"):
        from api.notification_service.app.schemas.notification import NotificationPreferencesUpdateDTO
        prefs_data = NotificationPreferencesUpdateDTO(email_enabled=False)
        result = notification_service.update_notification_preferences("user1", prefs_data)
        assert result.user_id == "user1" 