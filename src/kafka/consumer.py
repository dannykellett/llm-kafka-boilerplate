"""
Kafka consumer module for the LLM-Kafka Boilerplate.

This module provides a specialized consumer for Kafka messages with additional
functionality beyond the basic KafkaService.
"""

import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from src.config.config import KafkaSettings
from src.kafka.kafka_service import KafkaService, KafkaError

# Set up logging
logger = logging.getLogger(__name__)


class KafkaConsumerWorker:
    """
    Worker for consuming Kafka messages in a background thread.

    This class provides functionality for consuming Kafka messages in a background
    thread and processing them with a provided handler function.

    Attributes:
        kafka_service: Service for interacting with Kafka
        handler: Function to handle consumed messages
        poll_timeout: Maximum time to block waiting for a message (in seconds)
        worker_thread: Background thread for consuming messages
        running: Flag indicating whether the worker is running
    """

    def __init__(
        self,
        kafka_service: KafkaService,
        handler: Callable[[Dict[str, Any]], None],
        poll_timeout: float = 1.0,
    ):
        """
        Initialize the Kafka consumer worker.

        Args:
            kafka_service: Service for interacting with Kafka
            handler: Function to handle consumed messages
            poll_timeout: Maximum time to block waiting for a message (in seconds)
        """
        self.kafka_service = kafka_service
        self.handler = handler
        self.poll_timeout = poll_timeout
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        self._lock = threading.RLock()

    def start(self) -> None:
        """
        Start the consumer worker.

        This method starts a background thread for consuming messages.
        """
        with self._lock:
            if self.running:
                logger.warning("Consumer worker is already running")
                return

            self.running = True
            self.worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
            )
            self.worker_thread.start()
            logger.info("Started Kafka consumer worker")

    def stop(self) -> None:
        """
        Stop the consumer worker.

        This method stops the background thread for consuming messages.
        """
        with self._lock:
            if not self.running:
                logger.warning("Consumer worker is not running")
                return

            self.running = False
            logger.info("Stopping Kafka consumer worker")

    def _worker_loop(self) -> None:
        """
        Worker loop for consuming messages.

        This method runs in a background thread and continuously consumes
        messages from Kafka, passing them to the handler function.
        """
        try:
            # Start the Kafka consumer
            self.kafka_service.start_consumer()

            # Main processing loop
            while self.running:
                try:
                    # Consume a message
                    message = self.kafka_service.consume_message(self.poll_timeout)

                    # If a message was consumed, handle it
                    if message is not None:
                        try:
                            self.handler(message)
                        except Exception as e:
                            logger.error(f"Error handling message: {e}")
                except KafkaError as e:
                    logger.error(f"Kafka error in consumer worker: {e}")
                    # Sleep before retrying to avoid tight loop in case of persistent errors
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Unexpected error in consumer worker: {e}")
                    # Sleep before retrying to avoid tight loop in case of persistent errors
                    time.sleep(1)

        except Exception as e:
            logger.error(f"Fatal error in consumer worker: {e}")
        finally:
            # Ensure the consumer is stopped even if an exception occurs
            try:
                self.kafka_service.stop_consumer()
            except Exception as e:
                logger.error(f"Error stopping consumer: {e}")
