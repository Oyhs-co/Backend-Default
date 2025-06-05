import pytest
from unittest.mock import MagicMock, patch
from api.external_tools_service.app.services.external_tools_service import ExternalToolsService
from api.external_tools_service.app.schemas.external_tools import ExternalToolConnectionCreateDTO

@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()

@pytest.fixture
def external_tools_service(mock_db: MagicMock) -> ExternalToolsService:
    return ExternalToolsService(mock_db)

def test_create_connection_success(external_tools_service: ExternalToolsService):
    conn_data = ExternalToolConnectionCreateDTO(provider_id="prov1", access_token="token")
    mock_provider = MagicMock(id="prov1", type="github")
    mock_user_info = {"id": "user1", "name": "Test User", "email": "test@example.com"}
    with patch("api.shared.models.external_tools.ExternalToolConnection", MagicMock()), \
         patch("api.shared.models.external_tools.OAuthProvider", MagicMock()), \
         patch("api.shared.models.user.User", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(external_tools_service.db, "query") as mock_query, \
         patch.object(external_tools_service, "_connection_to_dto", return_value=MagicMock(id="conn1")), \
         patch.object(external_tools_service.adapter_factory, "create_adapter") as mock_adapter_factory:
        mock_adapter = MagicMock()
        mock_adapter.get_user_info.return_value = mock_user_info
        mock_adapter_factory.return_value = mock_adapter
        # Mock provider lookup
        mock_query.return_value.filter.return_value.first.side_effect = [mock_provider, None]
        external_tools_service.db.add = MagicMock()
        external_tools_service.db.commit = MagicMock()
        external_tools_service.db.refresh = MagicMock()
        result = external_tools_service.create_connection(conn_data, "user1")
        assert result.id == "conn1"

def test_get_user_connections(external_tools_service: ExternalToolsService):
    with patch("api.shared.models.external_tools.ExternalToolConnection", MagicMock()), \
         patch("api.shared.models.external_tools.OAuthProvider", MagicMock()), \
         patch("api.shared.models.user.User", MagicMock()), \
         patch("api.shared.models.project.ActivityLog", MagicMock()), \
         patch.object(external_tools_service.db, "query") as mock_query, \
         patch.object(external_tools_service, "_connection_to_dto", return_value=MagicMock(id="conn1")):
        mock_chain = MagicMock()
        mock_chain.filter.return_value = mock_chain
        mock_chain.all.return_value = [MagicMock()]
        mock_query.return_value = mock_chain
        result = external_tools_service.get_user_connections("user1")
        assert isinstance(result, list)
        assert result[0].id == "conn1"

def test_send_email_brevo_success(monkeypatch):
    from api.external_tools_service.app.services import email_tools
    class DummyApi:
        def send_transac_email(self, *a, **kw):
            return True
    monkeypatch.setenv("BREVO_API_KEY", "key")
    monkeypatch.setenv("BREVO_FROM", "from@example.com")
    monkeypatch.setattr(email_tools.sib_api_v3_sdk, "TransactionalEmailsApi", lambda *a, **kw: DummyApi())
    monkeypatch.setattr(email_tools.sib_api_v3_sdk, "ApiClient", lambda *a, **kw: None)
    assert email_tools.send_email_brevo("to@example.com", "subj", "body") is True

def test_send_email_brevo_fail(monkeypatch):
    from api.external_tools_service.app.services import email_tools
    monkeypatch.delenv("BREVO_API_KEY", raising=False)
    assert email_tools.send_email_brevo("to@example.com", "subj", "body") is False

def test_send_gotify_notification_success(monkeypatch):
    from api.external_tools_service.app.services import push_tools
    monkeypatch.setenv("GOTIFY_URL", "http://gotify")
    monkeypatch.setenv("GOTIFY_TOKEN", "token")
    monkeypatch.setattr(push_tools.requests, "post", lambda *a, **kw: type("Resp", (), {"status_code": 200})())
    assert push_tools.send_gotify_notification("msg", "title") is True

def test_send_gotify_notification_fail(monkeypatch):
    from api.external_tools_service.app.services import push_tools
    monkeypatch.delenv("GOTIFY_URL", raising=False)
    monkeypatch.delenv("GOTIFY_TOKEN", raising=False)
    assert push_tools.send_gotify_notification("msg", "title") is False

def test_send_sms_twilio_success(monkeypatch):
    from api.external_tools_service.app.services import sms_tools
    class DummyClient:
        def __init__(self, *a, **kw): pass
        class messages:
            @staticmethod
            def create(**kwargs): return True
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "sid")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+123")
    monkeypatch.setattr(sms_tools, "TwilioClient", DummyClient)
    assert sms_tools.send_sms_twilio("+456", "body") is True

def test_send_sms_twilio_fail(monkeypatch):
    from api.external_tools_service.app.services import sms_tools
    monkeypatch.setattr(sms_tools, "TwilioClient", None)
    assert sms_tools.send_sms_twilio("+456", "body") is False

def test_list_calendar_events(monkeypatch):
    from api.external_tools_service.app.services import calendar_tools
    class DummyCal:
        def events(self):
            class E: vobject_instance = type("V", (), {"vevent": type("Vev", (), {"summary": type("S", (), {"value": "event"})()})()})
            return [E()]
    class DummyPrincipal:
        def calendars(self): return [DummyCal()]
    class DummyClient:
        def principal(self): return DummyPrincipal()
    monkeypatch.setattr(calendar_tools, "get_caldav_client", lambda: DummyClient())
    result = calendar_tools.list_calendar_events()
    assert "events" in result
    assert result["events"] == ["event"]

def test_create_calendar_event(monkeypatch):
    from api.external_tools_service.app.services import calendar_tools
    class DummyCal:
        def add_event(self, ical): return True
    class DummyPrincipal:
        def calendars(self): return [DummyCal()]
    class DummyClient:
        def principal(self): return DummyPrincipal()
    monkeypatch.setattr(calendar_tools, "get_caldav_client", lambda: DummyClient())
    import datetime
    result = calendar_tools.create_calendar_event("summary", datetime.datetime.now(), datetime.datetime.now())
    assert result["status"] == "created"

def test_query_huggingface_success(monkeypatch):
    from api.external_tools_service.app.services import ai_tools
    monkeypatch.setenv("HUGGINGFACE_API_TOKEN", "token")
    class DummyResp:
        status_code = 200
        def json(self):
            return {"result": 1}
    monkeypatch.setattr(ai_tools.requests, "post", lambda *a, **kw: DummyResp())
    result = ai_tools.query_huggingface("model", {"input": 1})
    assert result == {"result": 1}

def test_query_huggingface_fail(monkeypatch):
    from api.external_tools_service.app.services import ai_tools
    monkeypatch.setenv("HUGGINGFACE_API_TOKEN", "token")
    class DummyResp:
        status_code = 400
        def json(self):
            return {"error": "fail"}
    monkeypatch.setattr(ai_tools.requests, "post", lambda *a, **kw: DummyResp())
    result = ai_tools.query_huggingface("model", {"input": 1})
    assert result is None

def test_get_metabase_card_data_success(monkeypatch):
    from api.external_tools_service.app.services import analytics_tools
    class DummyResp:
        status_code = 200
        def json(self):
            return {"data": 1}
    monkeypatch.setattr(analytics_tools.requests, "get", lambda *a, **kw: DummyResp())
    result = analytics_tools.get_metabase_card_data(1, "token", "http://mb")
    assert result == {"data": 1}

def test_get_metabase_card_data_fail(monkeypatch):
    from api.external_tools_service.app.services import analytics_tools
    class DummyResp:
        status_code = 400
        def json(self):
            return {"error": "fail"}
    monkeypatch.setattr(analytics_tools.requests, "get", lambda *a, **kw: DummyResp())
    result = analytics_tools.get_metabase_card_data(1, "token", "http://mb")
    assert result is None

def test_process_document_with_libreoffice_success(monkeypatch, tmp_path):
    from api.external_tools_service.app.services import document_tools
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")
    monkeypatch.setenv("LIBREOFFICE_ONLINE_URL", "http://lool/")
    monkeypatch.setattr(document_tools, "requests", MagicMock())
    document_tools.requests.post.return_value.status_code = 200
    document_tools.requests.post.return_value.content = b"pdfdata"
    monkeypatch.setattr(document_tools, "SupabaseManager", MagicMock())
    document_tools.SupabaseManager().get_client().storage().from_().upload.return_value = True
    document_tools.SupabaseManager().get_client().storage().from_().get_public_url.return_value = "http://url"
    result = document_tools.process_document_with_libreoffice(str(file_path), "pdf", "bucket", "path")
    assert result == "http://url"

def test_process_document_with_libreoffice_fail(monkeypatch, tmp_path):
    from api.external_tools_service.app.services import document_tools
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")
    monkeypatch.setenv("LIBREOFFICE_ONLINE_URL", "http://lool/")
    monkeypatch.setattr(document_tools, "requests", MagicMock())
    document_tools.requests.post.return_value.status_code = 400
    result = document_tools.process_document_with_libreoffice(str(file_path), "pdf")
    assert result is None 