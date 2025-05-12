"""
Tests for the app module.

This module contains tests for the main application functionality.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.app import App, SignalHandler, create_app


def test_signal_handler_initialization():
    """Test SignalHandler initialization."""
    handler = SignalHandler()
    assert handler.shutdown_requested is False


def test_signal_handler_request_shutdown():
    """Test SignalHandler request_shutdown method."""
    handler = SignalHandler()

    # Call request_shutdown
    handler.request_shutdown(signal=15, frame=None)

    # Verify that shutdown_requested is True
    assert handler.shutdown_requested is True


def test_signal_handler_register_handlers():
    """Test SignalHandler register_handlers method."""
    handler = SignalHandler()

    # Mock signal.signal
    with patch("signal.signal") as mock_signal:
        # Call register_handlers
        handler.register_handlers()

        # Verify that signal.signal was called twice
        assert mock_signal.call_count == 2


def test_app_initialization(
    mock_settings, mock_kafka_service, mock_llm_client, mock_processor_factory
):
    """Test App initialization."""
    # Create a mock metrics collector
    mock_metrics = MagicMock()

    # Create the app
    app = App(
        settings=mock_settings,
        kafka_service=mock_kafka_service,
        llm_client=mock_llm_client,
        processor_factory=mock_processor_factory,
        metrics=mock_metrics,
    )

    # Verify that the app was initialized correctly
    assert app.settings == mock_settings
    assert app.kafka_service == mock_kafka_service
    assert app.llm_client == mock_llm_client
    assert app.processor_factory == mock_processor_factory
    assert app.metrics == mock_metrics
    assert isinstance(app.signal_handler, SignalHandler)
    assert app.consumer_worker is None
    assert app.producer_worker is None


def test_app_initialize(
    mock_settings, mock_kafka_service, mock_llm_client, mock_processor_factory
):
    """Test App initialize method."""
    # Create a mock metrics collector
    mock_metrics = MagicMock()

    # Create the app
    app = App(
        settings=mock_settings,
        kafka_service=mock_kafka_service,
        llm_client=mock_llm_client,
        processor_factory=mock_processor_factory,
        metrics=mock_metrics,
    )

    # Mock the signal handler
    app.signal_handler = MagicMock()

    # Mock KafkaConsumerWorker and KafkaProducerWorker
    with patch("src.kafka.consumer.KafkaConsumerWorker") as mock_consumer_worker_class:
        with patch(
            "src.kafka.producer.KafkaProducerWorker"
        ) as mock_producer_worker_class:
            # Create mock instances
            mock_consumer_worker = MagicMock()
            mock_producer_worker = MagicMock()

            # Configure the mocks
            mock_consumer_worker_class.return_value = mock_consumer_worker
            mock_producer_worker_class.return_value = mock_producer_worker

            # Call initialize
            app.initialize()

            # Verify that the signal handler was registered
            app.signal_handler.register_handlers.assert_called_once()

            # Verify that the workers were created
            mock_consumer_worker_class.assert_called_once()
            mock_producer_worker_class.assert_called_once()

            # Verify that the workers were started
            mock_consumer_worker.start.assert_called_once()
            mock_producer_worker.start.assert_called_once()

            # Verify that the workers were assigned
            assert app.consumer_worker == mock_consumer_worker
            assert app.producer_worker == mock_producer_worker


def test_app_shutdown(
    mock_settings, mock_kafka_service, mock_llm_client, mock_processor_factory
):
    """Test App shutdown method."""
    # Create a mock metrics collector
    mock_metrics = MagicMock()

    # Create the app
    app = App(
        settings=mock_settings,
        kafka_service=mock_kafka_service,
        llm_client=mock_llm_client,
        processor_factory=mock_processor_factory,
        metrics=mock_metrics,
    )

    # Create mock workers
    app.consumer_worker = MagicMock()
    app.producer_worker = MagicMock()

    # Call shutdown
    app.shutdown()

    # Verify that the workers were stopped
    app.consumer_worker.stop.assert_called_once()
    app.producer_worker.stop.assert_called_once()

    # Verify that the Kafka service was closed
    mock_kafka_service.close.assert_called_once()


def test_app_handle_message(
    mock_settings,
    mock_kafka_service,
    mock_llm_client,
    mock_processor_factory,
    sample_message,
):
    """Test App handle_message method."""
    # Create a mock metrics collector
    mock_metrics = MagicMock()

    # Create the app
    app = App(
        settings=mock_settings,
        kafka_service=mock_kafka_service,
        llm_client=mock_llm_client,
        processor_factory=mock_processor_factory,
        metrics=mock_metrics,
    )

    # Create a mock processor
    mock_processor = MagicMock()
    mock_processor.handle.return_value = {"processed": True}

    # Configure the processor factory
    mock_processor_factory.create_processor.return_value = mock_processor

    # Create a mock producer worker
    app.producer_worker = MagicMock()

    # Call handle_message
    app.handle_message(sample_message)

    # Verify that the processor factory was called
    mock_processor_factory.create_processor.assert_called_once_with("test-type")

    # Verify that the processor was called
    mock_processor.handle.assert_called_once_with(sample_message)

    # Verify that the producer worker was called
    app.producer_worker.enqueue_message.assert_called_once()


def test_app_run(
    mock_settings, mock_kafka_service, mock_llm_client, mock_processor_factory
):
    """Test App run method."""
    # Create a mock metrics collector
    mock_metrics = MagicMock()

    # Create the app
    app = App(
        settings=mock_settings,
        kafka_service=mock_kafka_service,
        llm_client=mock_llm_client,
        processor_factory=mock_processor_factory,
        metrics=mock_metrics,
    )

    # Mock initialize and shutdown
    app.initialize = MagicMock()
    app.shutdown = MagicMock()

    # Configure the signal handler to request shutdown after one iteration
    app.signal_handler = MagicMock()
    app.signal_handler.shutdown_requested = False

    def side_effect():
        app.signal_handler.shutdown_requested = True

    app.signal_handler.shutdown_requested.__bool__ = MagicMock(
        side_effect=[False, True]
    )

    # Call run
    app.run()

    # Verify that initialize and shutdown were called
    app.initialize.assert_called_once()
    app.shutdown.assert_called_once()


def test_create_app():
    """Test create_app function."""
    # Mock get_settings
    mock_settings = MagicMock()
    with patch("src.app.get_settings", return_value=mock_settings):
        # Mock configure_logging
        with patch("src.utils.logging.configure_logging") as mock_configure_logging:
            # Mock KafkaService
            mock_kafka_service = MagicMock()
            with patch("src.app.KafkaService", return_value=mock_kafka_service):
                # Mock LLMClient
                mock_llm_client = MagicMock()
                with patch("src.app.LLMClient", return_value=mock_llm_client):
                    # Mock MetricsCollector
                    mock_metrics = MagicMock()
                    with patch(
                        "src.utils.metrics.MetricsCollector", return_value=mock_metrics
                    ):
                        # Mock ProcessorFactory
                        mock_processor_factory = MagicMock()
                        with patch(
                            "src.app.ProcessorFactory",
                            return_value=mock_processor_factory,
                        ):
                            # Call create_app
                            app = create_app()

                            # Verify that the app was created correctly
                            assert isinstance(app, App)
                            assert app.settings == mock_settings
                            assert app.kafka_service == mock_kafka_service
                            assert app.llm_client == mock_llm_client
                            assert app.processor_factory == mock_processor_factory
                            assert app.metrics == mock_metrics
