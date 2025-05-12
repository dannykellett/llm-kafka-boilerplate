"""
Pytest configuration for the LLM-Kafka Boilerplate.

This module provides fixtures for testing the boilerplate.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from src.config.config import Settings, KafkaSettings, LLMSettings, ApplicationSettings
from src.kafka.kafka_service import KafkaService
from src.llm.client import LLMClient
from src.processing.processor_factory import ProcessorFactory


@pytest.fixture
def mock_settings():
    """
    Fixture for mock settings.

    Returns:
        Settings: Mock settings for testing
    """
    return Settings(
        kafka=KafkaSettings(
            bootstrap_servers="localhost:9092",
            input_topic="input-topic",
            output_topic="output-topic",
            group_id="test-group",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        ),
        llm=LLMSettings(
            api_key="test-api-key",
            api_url="https://api.test.com/v1/completions",
            model="test-model",
            temperature=0.2,
            max_tokens=500,
        ),
        app=ApplicationSettings(
            log_level="INFO",
            cache_ttl_seconds=3600,
        ),
    )


@pytest.fixture
def mock_kafka_service():
    """
    Fixture for mock Kafka service.

    Returns:
        MagicMock: Mock Kafka service for testing
    """
    mock_service = MagicMock(spec=KafkaService)
    mock_service.consume_message.return_value = None
    return mock_service


@pytest.fixture
def mock_llm_client():
    """
    Fixture for mock LLM client.

    Returns:
        MagicMock: Mock LLM client for testing
    """
    mock_client = MagicMock(spec=LLMClient)
    mock_client.generate.return_value = "Test response"
    mock_client.get_metrics.return_value = {"token_usage": 10}
    return mock_client


@pytest.fixture
def mock_processor_factory(mock_settings, mock_llm_client):
    """
    Fixture for mock processor factory.

    Args:
        mock_settings: Mock settings
        mock_llm_client: Mock LLM client

    Returns:
        ProcessorFactory: Mock processor factory for testing
    """
    return ProcessorFactory(mock_settings, mock_llm_client)


@pytest.fixture
def sample_message():
    """
    Fixture for a sample message.

    Returns:
        dict: Sample message for testing
    """
    return {
        "id": "test-id",
        "type": "test-type",
        "content": "Test content",
        "metadata": {
            "source": "test",
            "timestamp": "2025-05-12T14:30:00Z",
        },
    }


@pytest.fixture
def env_vars():
    """
    Fixture for setting environment variables for testing.

    Yields:
        None
    """
    # Save original environment variables
    original_env = os.environ.copy()

    # Set test environment variables
    os.environ.update(
        {
            "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
            "KAFKA_INPUT_TOPIC": "input-topic",
            "KAFKA_OUTPUT_TOPIC": "output-topic",
            "KAFKA_GROUP_ID": "test-group",
            "KAFKA_AUTO_OFFSET_RESET": "earliest",
            "KAFKA_ENABLE_AUTO_COMMIT": "true",
            "LLM_API_KEY": "test-api-key",
            "LLM_API_URL": "https://api.test.com/v1/completions",
            "LLM_MODEL": "test-model",
            "LLM_TEMPERATURE": "0.2",
            "LLM_MAX_TOKENS": "500",
            "LOG_LEVEL": "INFO",
            "CACHE_TTL_SECONDS": "3600",
        }
    )

    yield

    # Restore original environment variables
    os.environ.clear()
    os.environ.update(original_env)
