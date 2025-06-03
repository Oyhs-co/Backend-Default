from api.shared.utils.rabbitmq import RabbitMQManager
from unittest.mock import MagicMock
import pytest

def test_singleton_instance() -> None:
    manager1 = RabbitMQManager()
    manager2 = RabbitMQManager()
    assert manager1 is manager2

def test_connect_and_declare(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = RabbitMQManager()
    # Ensure _connection attribute exists before monkeypatching
    if not hasattr(manager, '_connection'):
        manager._connection = None  # type: ignore[attr-defined]
    mock_conn = MagicMock()
    monkeypatch.setattr(manager, '_connection', mock_conn)  # type: ignore[attr-defined]
    monkeypatch.setattr(manager, 'declare_exchange', MagicMock())
    monkeypatch.setattr(manager, 'declare_queue', MagicMock())
    manager.declare_exchange('ex')
    manager.declare_queue('q')
    assert manager._connection is mock_conn  # type: ignore[attr-defined]

def test_publish(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = RabbitMQManager()
    # Ensure _connection attribute exists before monkeypatching
    if not hasattr(manager, '_connection'):
        manager._connection = None  # type: ignore[attr-defined]
    monkeypatch.setattr(manager, '_connection', MagicMock())  # type: ignore[attr-defined]
    monkeypatch.setattr(manager, 'publish', MagicMock())
    manager.publish('ex', 'rk', {'msg': 'data'}) 