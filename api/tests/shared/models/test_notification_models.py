from api.shared.models.notification import Notification, NotificationPreference
from datetime import datetime

def test_notification_model_instantiation() -> None:
    notif = Notification(
        id='nid', user_id='uid', type='system', title='T', message='M', priority='normal', channels=['in_app'], created_at=datetime.now()
    )
    assert notif.user_id == 'uid'
    assert notif.type == 'system'
    assert notif.title == 'T'
    assert notif.priority == 'normal'
    assert 'in_app' in notif.channels
    assert notif.is_read in (None, False)

def test_notification_preference_model_instantiation() -> None:
    pref = NotificationPreference(
        user_id='uid',
        email_enabled=True,
        push_enabled=True,
        sms_enabled=False,
        in_app_enabled=True,
        digest_enabled=False
    )
    assert pref.user_id == 'uid'
    assert pref.email_enabled is True
    assert pref.push_enabled is True
    assert pref.sms_enabled is False
    assert pref.in_app_enabled is True
    assert pref.digest_enabled is False 