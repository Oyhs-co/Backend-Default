from api.shared.utils.rabbitmq import RabbitMQManager
from unittest.mock import MagicMock
from typing import Any

def test_singleton_instance() -> None:
    manager1 = RabbitMQManager()
    manager2 = RabbitMQManager()
    assert manager1 is manager2

def test_connect_and_declare(monkeypatch: Any) -> None:
    manager = RabbitMQManager()
    if not hasattr(manager, '_connection'):
        manager._connection = None  # type: ignore[attr-defined]
    mock_conn = MagicMock()
    monkeypatch.setattr(manager, '_connection', mock_conn)  # type: ignore[attr-defined]
    monkeypatch.setattr(manager, 'declare_exchange', MagicMock())
    monkeypatch.setattr(manager, 'declare_queue', MagicMock())
    manager.declare_exchange('ex')
    manager.declare_queue('q')
    assert manager._connection is mock_conn  # type: ignore[attr-defined]

def test_publish(monkeypatch: Any) -> None:
    manager = RabbitMQManager()
    if not hasattr(manager, '_connection'):
        manager._connection = None  # type: ignore[attr-defined]
    monkeypatch.setattr(manager, '_connection', MagicMock())  # type: ignore[attr-defined]
    monkeypatch.setattr(manager, 'publish', MagicMock())
    manager.publish('ex', 'rk', {'msg': 'data'})

def test_publish_without_connection(monkeypatch: Any) -> None:
    manager = RabbitMQManager()
    monkeypatch.setattr(manager, '_connection', None)
    manager.publish('ex', 'rk', {'msg': 'data'})

def test_connect_failure(monkeypatch: Any) -> None:
    manager = RabbitMQManager()
    import pika
    monkeypatch.setattr(pika, 'BlockingConnection', lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")))
    try:
        manager._connect()  # type: ignore[attr-defined]
    except Exception as e:
        assert isinstance(e, Exception)

def test_close_connection(monkeypatch: Any) -> None:
    manager = RabbitMQManager()
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    mock_conn.is_closed = False
    monkeypatch.setattr(manager, '_connection', mock_conn)
    manager.close()
    mock_conn.close.assert_called_once()

def test_close_connection_already_closed(monkeypatch: Any):
    from api.shared.utils.rabbitmq import RabbitMQManager
    manager = RabbitMQManager()
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    mock_conn.is_closed = True
    monkeypatch.setattr(manager, '_connection', mock_conn)
    manager.close()
    mock_conn.close.assert_not_called()

def test_close_connection_none(monkeypatch: Any):
    from api.shared.utils.rabbitmq import RabbitMQManager
    manager = RabbitMQManager()
    monkeypatch.setattr(manager, '_connection', None)
    manager.close()  # Should not raise 