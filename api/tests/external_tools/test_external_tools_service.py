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