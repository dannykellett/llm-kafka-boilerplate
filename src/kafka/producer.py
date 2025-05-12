"""
Kafka producer module for the LLM-Kafka Boilerplate.

This module provides a specialized producer for Kafka messages with additional
functionality beyond the basic KafkaService.
"""

import logging
import threading
import queue
from typing import Any, Callable, Dict, List, Optional, Union

from src.config.config import KafkaSettings
from src.kafka.kafka_service import KafkaService, KafkaError, MessageSerializationError

# Set up logging
logger = logging.getLogger(__name__)


class KafkaProducerWorker:
    """
    Worker for producing Kafka messages with a queue.

    This class provides functionality for producing Kafka messages using a queue,
    which can be useful for asynchronous message production.

    Attributes:
        kafka_service: Service for interacting with Kafka
        message_queue: Queue for messages to be produced
        worker_thread: Background thread for producing messages
        running: Flag indicating whether the worker is running
        max_queue_size: Maximum size of the message queue
    """

    def __init__(
        self,
        kafka_service: KafkaService,
        max_queue_size: int = 1000,
    ):
        """
        Initialize the Kafka producer worker.

        Args:
            kafka_service: Service for interacting with Kafka
            max_queue_size: Maximum size of the message queue
        """
        self.kafka_service = kafka_service
        self.message_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        self._lock = threading.RLock()

    def start(self) -> None:
        """
        Start the producer worker.

        This method starts a background thread for producing messages.
        """
        with self._lock:
            if self.running:
                logger.warning("Producer worker is already running")
                return

            self.running = True
            self.worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
            )
            self.worker_thread.start()
            logger.info("Started Kafka producer worker")

    def stop(self) -> None:
        """
        Stop the producer worker.

        This method stops the background thread for producing messages.
        """
        with self._lock:
            if not self.running:
                logger.warning("Producer worker is not running")
                return

            self.running = False
            logger.info("Stopping Kafka producer worker")

            # Wait for the worker thread to finish
            if self.worker_thread is not None and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=5.0)
                if self.worker_thread.is_alive():
                    logger.warning("Producer worker thread did not terminate")

    def enqueue_message(self, message: Dict[str, Any]) -> bool:
        """
        Enqueue a message for production.

        Args:
            message: The message to produce

        Returns:
            bool: True if the message was enqueued, False otherwise
        """
        try:
            self.message_queue.put(message, block=False)
            return True
        except queue.Full:
            logger.warning("Message queue is full, message not enqueued")
            return False

    def _worker_loop(self) -> None:
        """
        Worker loop for producing messages.

        This method runs in a background thread and continuously produces
        messages from the queue to Kafka.
        """
        try:
            # Main processing loop
            while self.running or not self.message_queue.empty():
                try:
                    # Get a message from the queue with a timeout
                    try:
                        message = self.message_queue.get(block=True, timeout=1.0)
                    except queue.Empty:
                        # If the queue is empty, continue the loop
                        continue

                    # Produce the message
                    try:
                        self.kafka_service.produce_message(message)
                        self.message_queue.task_done()
                    except (KafkaError, MessageSerializationError) as e:
                        logger.error(f"Error producing message: {e}")
                        # Mark the task as done even if it failed
                        self.message_queue.task_done()
                except Exception as e:
                    logger.error(f"Unexpected error in producer worker: {e}")

            # Flush the producer before exiting
            self.kafka_service.flush_producer()

        except Exception as e:
            logger.error(f"Fatal error in producer worker: {e}")
        finally:
            # Ensure the producer is flushed even if an exception occurs
            try:
                self.kafka_service.flush_producer()
            except Exception as e:
                logger.error(f"Error flushing producer: {e}")
