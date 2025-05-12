"""
Main application module for the LLM-Kafka Boilerplate.

This module provides the main entry point for the application and orchestrates
the entire workflow from consuming Kafka messages to producing results.
It handles initialization, graceful shutdown, and error handling.
"""

import os
import signal
import time
import logging
from typing import Optional, Dict, Any

from src.config.config import Settings, get_settings
from src.kafka.kafka_service import KafkaService, KafkaError
from src.kafka.consumer import KafkaConsumerWorker
from src.kafka.producer import KafkaProducerWorker
from src.llm.client import LLMClient, LLMProviderError
from src.processing.processor import ProcessingError
from src.processing.processor_factory import ProcessorFactory
from src.utils.logging import configure_logging
from src.utils.metrics import MetricsCollector

# Set up logging
logger = logging.getLogger(__name__)


class SignalHandler:
    """
    Handler for system signals.

    This class provides methods for handling system signals such as SIGINT and SIGTERM,
    allowing for graceful shutdown of the application.

    Attributes:
        shutdown_requested: Flag indicating whether shutdown has been requested.
    """

    def __init__(self):
        """Initialize the signal handler."""
        self.shutdown_requested = False

    def request_shutdown(self, signum, frame):
        """
        Request application shutdown.

        This method is called when a signal is received, and sets the
        shutdown_requested flag to True.

        Args:
            signum: Signal number.
            frame: Current stack frame.
        """
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True

    def register_handlers(self):
        """
        Register signal handlers.

        This method registers handlers for SIGINT and SIGTERM signals.
        """
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)
        logger.info("Registered signal handlers for graceful shutdown")


class App:
    """
    Main application class.

    This class orchestrates the entire workflow of the application, from
    consuming Kafka messages to producing results.

    Attributes:
        settings: Application settings.
        kafka_service: Service for interacting with Kafka.
        llm_client: Client for interacting with the LLM.
        processor_factory: Factory for creating processors.
        metrics: Metrics collector.
        signal_handler: Handler for system signals.
        consumer_worker: Worker for consuming Kafka messages.
        producer_worker: Worker for producing Kafka messages.
    """

    def __init__(
        self,
        settings: Settings,
        kafka_service: KafkaService,
        llm_client: LLMClient,
        processor_factory: ProcessorFactory,
        metrics: MetricsCollector,
    ):
        """
        Initialize the application.

        Args:
            settings: Application settings.
            kafka_service: Service for interacting with Kafka.
            llm_client: Client for interacting with the LLM.
            processor_factory: Factory for creating processors.
            metrics: Metrics collector.
        """
        self.settings = settings
        self.kafka_service = kafka_service
        self.llm_client = llm_client
        self.processor_factory = processor_factory
        self.metrics = metrics
        self.signal_handler = SignalHandler()
        self.consumer_worker: Optional[KafkaConsumerWorker] = None
        self.producer_worker: Optional[KafkaProducerWorker] = None

    def initialize(self):
        """
        Initialize application components.

        This method initializes all components of the application, including
        registering signal handlers, creating workers, and starting them.
        """
        logger.info("Initializing application...")

        # Register signal handlers
        self.signal_handler.register_handlers()

        # Create consumer worker
        self.consumer_worker = KafkaConsumerWorker(
            kafka_service=self.kafka_service,
            handler=self.handle_message,
        )

        # Create producer worker
        self.producer_worker = KafkaProducerWorker(
            kafka_service=self.kafka_service,
        )

        # Start workers
        self.consumer_worker.start()
        self.producer_worker.start()

        logger.info("Application initialized successfully")

    def shutdown(self):
        """
        Shutdown application components.

        This method gracefully shuts down all components of the application,
        including stopping workers and closing the Kafka service.
        """
        logger.info("Shutting down application...")

        # Stop workers
        if self.consumer_worker:
            self.consumer_worker.stop()
            logger.info("Stopped consumer worker")

        if self.producer_worker:
            self.producer_worker.stop()
            logger.info("Stopped producer worker")

        # Close Kafka service
        self.kafka_service.close()
        logger.info("Closed Kafka service")

        logger.info("Application shutdown complete")

    def handle_message(self, message: Dict[str, Any]) -> None:
        """
        Handle a message from Kafka.

        This method processes a message from Kafka using the appropriate processor,
        and produces the result to the output topic.

        Args:
            message: The message to handle
        """
        try:
            # Start timing
            self.metrics.start_timer("message_processing")

            # Get message type
            message_type = message.get("type", "default")
            logger.info(f"Processing message of type: {message_type}")

            # Create processor for message type
            processor = self.processor_factory.create_processor(message_type)

            # Process message
            result = processor.handle(message)

            # Add metrics to result
            result["metrics"] = self.metrics.get_metrics()

            # Produce result to output topic
            self.producer_worker.enqueue_message(result)
            logger.info(f"Produced result for message of type: {message_type}")

            # Stop timing and record metrics
            processing_time = self.metrics.stop_timer("message_processing")
            if processing_time:
                logger.info(f"Processed message in {processing_time:.3f} seconds")

        except ProcessingError as e:
            logger.error(f"Processing error: {e}")
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        except LLMProviderError as e:
            logger.error(f"LLM provider error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def run(self):
        """
        Run the application.

        This method runs the main loop of the application, waiting for shutdown
        to be requested.
        """
        try:
            # Initialize application
            self.initialize()

            logger.info("Application running, press Ctrl+C to stop")

            # Main loop
            while not self.signal_handler.shutdown_requested:
                # Sleep to avoid busy waiting
                time.sleep(1)

            logger.info("Shutdown requested, exiting main loop")

        except Exception as e:
            logger.error(f"Fatal error in application: {e}")
        finally:
            # Ensure shutdown is called even if an exception occurs
            self.shutdown()


def create_app() -> App:
    """
    Create and configure the application.

    This factory function creates and configures all components of the application,
    including loading settings, creating services, and wiring everything together.

    Returns:
        App: The configured application instance.
    """
    # Load settings
    settings = get_settings()

    # Configure logging
    configure_logging(log_level=settings.app.log_level)

    # Create Kafka service
    kafka_service = KafkaService(settings.kafka)

    # Create LLM client
    llm_client = LLMClient(settings)

    # Create metrics collector
    metrics = MetricsCollector()

    # Create processor factory
    processor_factory = ProcessorFactory(settings, llm_client)

    # Create and return application
    return App(settings, kafka_service, llm_client, processor_factory, metrics)


def main():
    """
    Main entry point for the application.

    This function creates and runs the application.
    """
    logger.info("Starting LLM-Kafka Boilerplate")

    # Create application
    app = create_app()

    # Run application
    app.run()

    logger.info("LLM-Kafka Boilerplate exited")


if __name__ == "__main__":
    main()
