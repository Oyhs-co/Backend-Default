import pytest
from unittest.mock import MagicMock, patch
from api.document_service.app.decorators import document_decorators
from api.shared.exceptions.document_exceptions import DocumentNotFoundException, InsufficientDocumentPermissionException
from typing import Any

class DummyService:
    def __init__(self, db: Any) -> None:
        self.db = db
    def _has_permission(self, document_id: str, user_id: str, permission_type: str) -> bool:
        return permission_type == 'view' and user_id == 'allowed'

@pytest.fixture
def db_mock() -> MagicMock:
    db = MagicMock()
    return db

def test_document_exists_found(db_mock: MagicMock) -> None:
    db_mock.query().filter().first.return_value = object()
    @document_decorators.document_exists
    def func(self: Any, document_id: str) -> str:
        return 'ok'
    service = DummyService(db_mock)
    assert func(service, 'docid') == 'ok'

def test_document_exists_not_found(db_mock: MagicMock) -> None:
    db_mock.query().filter().first.return_value = None
    @document_decorators.document_exists
    def func(self: Any, document_id: str) -> str:
        return 'ok'
    service = DummyService(db_mock)
    with pytest.raises(DocumentNotFoundException):
        func(service, 'docid')

def test_require_permission_granted(db_mock: MagicMock) -> None:
    @document_decorators.require_permission('view')
    def func(self: Any, document_id: str, user_id: str) -> str:
        return 'ok'
    service = DummyService(db_mock)
    assert func(service, 'docid', 'allowed') == 'ok'

def test_require_permission_denied(db_mock: MagicMock) -> None:
    @document_decorators.require_permission('edit')
    def func(self: Any, document_id: str, user_id: str) -> str:
        return 'fail'
    service = DummyService(db_mock)
    with pytest.raises(InsufficientDocumentPermissionException):
        func(service, 'docid', 'notallowed')

def test_log_document_activity(db_mock: MagicMock) -> None:
    db_mock.query().filter().first.return_value = MagicMock(project_id='pid', name='docname')
    with patch('api.project_service.app.services.activity_service.ActivityService') as mock_activity:
        @document_decorators.log_document_activity('edit')
        def func(self: Any, document_id: str, user_id: str) -> str:
            return 'done'
        service = DummyService(db_mock)
        result = func(service, 'docid', 'uid')
        assert result == 'done'
        mock_activity.assert_called()

def test_cache_document(db_mock: MagicMock) -> None:
    calls: list[str] = []
    @document_decorators.cache_document
    def func(self: Any, document_id: str) -> str:
        calls.append(document_id)
        return f'doc-{document_id}'
    service = DummyService(db_mock)
    # First call caches
    assert func(service, 'docid') == 'doc-docid'
    # Second call uses cache (no new append)
    assert func(service, 'docid') == 'doc-docid'
    assert calls == ['docid'] 