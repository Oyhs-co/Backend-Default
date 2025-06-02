import json
import logging
import os
import threading
from typing import Any, Callable, Dict, Optional

import pika
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQManager:
    """Singleton class for managing RabbitMQ connections"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> Any:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RabbitMQManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self) -> Any:
        """Initialize RabbitMQ connection"""
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self) -> Any:
        """Connect to RabbitMQ server"""
        try:
            # Create connection parameters
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                virtual_host=RABBITMQ_VHOST,
                credentials=credentials,
            )

            # Connect to RabbitMQ server
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            logger.info("Connected to RabbitMQ server")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ server: {e}")
            self.connection = None
            self.channel = None

    def ensure_connection(self) -> Any:
        """Ensure connection to RabbitMQ server"""
        if self.connection is None or self.connection.is_closed:
            self.connect()

    def declare_exchange(
        self, exchange_name: str, exchange_type: str = "topic", durable: bool = True
    ) -> Any:
        """
        Declare an exchange.

        Args:
            exchange_name (str): Exchange name
            exchange_type (str, optional): Exchange type. Defaults to "topic".
            durable (bool, optional): Whether the exchange should survive broker restarts. Defaults to True.
        """
        self.ensure_connection()
        if self.channel:
            self.channel.exchange_declare(
                exchange=exchange_name, exchange_type=exchange_type, durable=durable
            )

    def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Declare a queue.

        Args:
            queue_name (str): Queue name
            durable (bool, optional): Whether the queue should survive broker restarts. Defaults to True.
            arguments (Dict[str, Any], optional): Additional arguments for the queue. Defaults to None.
        """
        self.ensure_connection()
        if self.channel:
            self.channel.queue_declare(
                queue=queue_name, durable=durable, arguments=arguments
            )

    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str) -> Any:
        """
        Bind a queue to an exchange.

        Args:
            queue_name (str): Queue name
            exchange_name (str): Exchange name
            routing_key (str): Routing key
        """
        self.ensure_connection()
        if self.channel:
            self.channel.queue_bind(
                queue=queue_name, exchange=exchange_name, routing_key=routing_key
            )

    def publish(
        self,
        exchange_name: str,
        routing_key: str,
        message: Dict[str, Any],
        persistent: bool = True,
    ) -> Any:
        """
        Publish a message to an exchange.

        Args:
            exchange_name (str): Exchange name
            routing_key (str): Routing key
            message (Dict[str, Any]): Message to publish
            persistent (bool, optional): Whether the message should be persistent. Defaults to True.
        """
        self.ensure_connection()
        if self.channel:
            properties = pika.BasicProperties(
                delivery_mode=2 if persistent else 1,  # 2 means persistent
                content_type="application/json",
            )

            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=properties,
            )

    def consume(
        self,
        queue_name: str,
        callback: Callable[[Dict[str, Any]], None],
        auto_ack: bool = True,
    ) -> Any:
        """
        Consume messages from a queue.

        Args:
            queue_name (str): Queue name
            callback (Callable[[Dict[str, Any]], None]): Callback function to process messages
            auto_ack (bool, optional): Whether to automatically acknowledge messages. Defaults to True.
        """
        self.ensure_connection()
        if self.channel:

            def on_message(ch, method, properties, body) -> Any:
                try:
                    message = json.loads(body)
                    callback(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            self.channel.basic_consume(
                queue=queue_name, on_message_callback=on_message, auto_ack=auto_ack
            )

            self.channel.start_consuming()

    def close(self) -> Any:
        """Close RabbitMQ connection"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")
