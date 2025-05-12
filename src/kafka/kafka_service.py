"""
Kafka service module for the LLM-Kafka Boilerplate.

This module provides a service for interacting with Kafka, including consuming
messages from the input topic and producing messages to the output topic.
It handles message serialization/deserialization, error handling, and connection management.
"""

import json
import logging
from typing import Any, Callable, Dict, Optional, Union

from confluent_kafka import Consumer, KafkaException, Producer

from src.config.config import KafkaSettings

# Set up logging
logger = logging.getLogger(__name__)


class KafkaError(Exception):
    """Exception raised for Kafka-related errors."""

    pass


class MessageSerializationError(Exception):
    """Exception raised for message serialization/deserialization errors."""

    pass


class KafkaService:
    """
    Service for interacting with Kafka.

    This class provides methods for consuming messages from the input topic
    and producing messages to the output topic. It handles message
    serialization/deserialization, error handling, and connection management.

    Attributes:
        settings: Kafka configuration settings
        input_topic: Name of the input Kafka topic
        output_topic: Name of the output Kafka topic
        consumer: Kafka consumer instance
        producer: Kafka producer instance
    """

    def __init__(self, settings: KafkaSettings):
        """
        Initialize the Kafka service.

        Args:
            settings: Kafka configuration settings
        """
        self.settings = settings
        self.input_topic = settings.input_topic
        self.output_topic = settings.output_topic

        # Initialize consumer
        consumer_config = {
            "bootstrap.servers": settings.bootstrap_servers,
            "group.id": settings.group_id,
            "auto.offset.reset": settings.auto_offset_reset,
            "enable.auto.commit": settings.enable_auto_commit,
        }

        logger.info(f"Creating Kafka consumer with config: {consumer_config}")
        self.consumer = Consumer(consumer_config)

        # Initialize producer
        self.producer = Producer(
            {
                "bootstrap.servers": settings.bootstrap_servers,
            }
        )

        logger.info(
            "Initialized Kafka service with input topic %s and output topic %s",
            self.input_topic,
            self.output_topic,
        )

    def start_consumer(self) -> None:
        """
        Start the Kafka consumer by subscribing to the input topic.
        """
        try:
            self.consumer.subscribe([self.input_topic])
            logger.info("Subscribed to topic: %s", self.input_topic)
        except KafkaException as e:
            error_msg = f"Error subscribing to topic {self.input_topic}: {str(e)}"
            logger.error(error_msg)
            raise KafkaError(error_msg) from e

    def stop_consumer(self) -> None:
        """
        Stop the Kafka consumer.
        """
        try:
            self.consumer.close()
            logger.info("Closed Kafka consumer")
        except KafkaException as e:
            error_msg = f"Error closing Kafka consumer: {str(e)}"
            logger.error(error_msg)
            raise KafkaError(error_msg) from e

    def consume_message(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Consume a message from the input topic.

        Args:
            timeout: Maximum time to block waiting for a message (in seconds)

        Returns:
            The consumed message as a dictionary, or None if no message is available

        Raises:
            KafkaError: If there is an error consuming the message
            MessageSerializationError: If there is an error deserializing the message
        """
        try:
            # Poll for a message
            logger.debug(
                f"Polling Kafka topic {self.input_topic} with timeout {timeout}s"
            )
            message = self.consumer.poll(timeout)

            # If no message is available, return None
            if message is None:
                logger.debug("Kafka poll returned None (no message available)")
                return None

            # Check for errors
            if message.error():
                error_msg = f"Error consuming message: {message.error()}"
                logger.error(error_msg)
                raise KafkaError(error_msg)

            # Deserialize the message
            try:
                message_value = message.value().decode("utf-8")
                deserialized_message = json.loads(message_value)
                logger.debug("Consumed message: %s", deserialized_message)
                return deserialized_message
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                error_msg = f"Error deserializing message: {str(e)}"
                logger.error(error_msg)
                raise MessageSerializationError(error_msg) from e

        except KafkaException as e:
            error_msg = f"Kafka error while consuming message: {str(e)}"
            logger.error(error_msg)
            raise KafkaError(error_msg) from e

    def produce_message(
        self, message: Dict[str, Any], callback: Optional[Callable] = None
    ) -> None:
        """
        Produce a message to the output topic.

        Args:
            message: The message to produce
            callback: Optional callback function to call when the message is delivered

        Raises:
            MessageSerializationError: If there is an error serializing the message
            KafkaError: If there is an error producing the message
        """
        try:
            # Serialize the message
            try:
                serialized_message = json.dumps(message).encode("utf-8")
            except (TypeError, ValueError) as e:
                error_msg = f"Error serializing message: {str(e)}"
                logger.error(error_msg)
                raise MessageSerializationError(error_msg) from e

            # Produce the message
            try:
                self.producer.produce(
                    self.output_topic, serialized_message, callback=callback
                )
                logger.debug(
                    "Produced message to topic %s: %s", self.output_topic, message
                )
            except KafkaException as e:
                error_msg = (
                    f"Error producing message to topic {self.output_topic}: {str(e)}"
                )
                logger.error(error_msg)
                raise KafkaError(error_msg) from e

        except MessageSerializationError:
            # Re-raise MessageSerializationError without wrapping it in KafkaError
            raise
        except Exception as e:
            error_msg = f"Unexpected error producing message: {str(e)}"
            logger.error(error_msg)
            raise KafkaError(error_msg) from e

    def flush_producer(self, timeout: float = 5.0) -> None:
        """
        Flush the producer to ensure all messages are delivered.

        Args:
            timeout: Maximum time to block (in seconds)

        Raises:
            KafkaError: If there is an error flushing the producer
        """
        try:
            remaining = self.producer.flush(timeout)
            if remaining > 0:
                logger.warning(
                    "%d messages still in queue after flush timeout", remaining
                )
        except KafkaException as e:
            error_msg = f"Error flushing producer: {str(e)}"
            logger.error(error_msg)
            raise KafkaError(error_msg) from e

    def close(self) -> None:
        """
        Close the Kafka service, including the consumer and producer.

        This method should be called when the service is no longer needed
        to ensure proper cleanup of resources.
        """
        try:
            # Close the consumer
            self.consumer.close()
            logger.info("Closed Kafka consumer")

            # Flush the producer
            self.producer.flush()
            logger.info("Flushed Kafka producer")
        except KafkaException as e:
            error_msg = f"Error closing Kafka service: {str(e)}"
            logger.error(error_msg)
            raise KafkaError(error_msg) from e

    def __enter__(self) -> "KafkaService":
        """
        Enter the context manager.

        Returns:
            The KafkaService instance
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.close()
