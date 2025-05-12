"""
Tests for the config module.

This module contains tests for the configuration management functionality.
"""

import os
import pytest
from unittest.mock import patch

from src.config.config import (
    Settings,
    get_settings,
    KafkaSettings,
    LLMSettings,
    ApplicationSettings,
)


def test_kafka_settings_validation():
    """Test KafkaSettings validation."""
    # Valid settings
    valid_settings = KafkaSettings(
        bootstrap_servers="localhost:9092",
        input_topic="input-topic",
        output_topic="output-topic",
        group_id="test-group",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    assert valid_settings.bootstrap_servers == "localhost:9092"
    assert valid_settings.input_topic == "input-topic"
    assert valid_settings.output_topic == "output-topic"
    assert valid_settings.group_id == "test-group"
    assert valid_settings.auto_offset_reset == "earliest"
    assert valid_settings.enable_auto_commit is True

    # Invalid bootstrap_servers
    with pytest.raises(ValueError):
        KafkaSettings(
            bootstrap_servers="",
            input_topic="input-topic",
            output_topic="output-topic",
            group_id="test-group",
        )

    # Invalid input_topic
    with pytest.raises(ValueError):
        KafkaSettings(
            bootstrap_servers="localhost:9092",
            input_topic="",
            output_topic="output-topic",
            group_id="test-group",
        )

    # Invalid output_topic
    with pytest.raises(ValueError):
        KafkaSettings(
            bootstrap_servers="localhost:9092",
            input_topic="input-topic",
            output_topic="",
            group_id="test-group",
        )

    # Invalid group_id
    with pytest.raises(ValueError):
        KafkaSettings(
            bootstrap_servers="localhost:9092",
            input_topic="input-topic",
            output_topic="output-topic",
            group_id="",
        )

    # Invalid auto_offset_reset
    with pytest.raises(ValueError):
        KafkaSettings(
            bootstrap_servers="localhost:9092",
            input_topic="input-topic",
            output_topic="output-topic",
            group_id="test-group",
            auto_offset_reset="invalid",
        )


def test_llm_settings_validation():
    """Test LLMSettings validation."""
    # Valid settings
    valid_settings = LLMSettings(
        api_key="test-api-key",
        api_url="https://api.test.com/v1/completions",
        model="test-model",
        temperature=0.2,
        max_tokens=500,
    )
    assert valid_settings.api_key == "test-api-key"
    assert str(valid_settings.api_url) == "https://api.test.com/v1/completions"
    assert valid_settings.model == "test-model"
    assert valid_settings.temperature == 0.2
    assert valid_settings.max_tokens == 500

    # Invalid api_key
    with pytest.raises(ValueError):
        LLMSettings(
            api_key="",
            api_url="https://api.test.com/v1/completions",
            model="test-model",
        )

    # Invalid api_url
    with pytest.raises(ValueError):
        LLMSettings(
            api_key="test-api-key",
            api_url="invalid-url",
            model="test-model",
        )

    # Invalid model
    with pytest.raises(ValueError):
        LLMSettings(
            api_key="test-api-key",
            api_url="https://api.test.com/v1/completions",
            model="",
        )

    # Invalid temperature
    with pytest.raises(ValueError):
        LLMSettings(
            api_key="test-api-key",
            api_url="https://api.test.com/v1/completions",
            model="test-model",
            temperature=1.5,
        )

    # Invalid max_tokens
    with pytest.raises(ValueError):
        LLMSettings(
            api_key="test-api-key",
            api_url="https://api.test.com/v1/completions",
            model="test-model",
            max_tokens=0,
        )


def test_application_settings_validation():
    """Test ApplicationSettings validation."""
    # Valid settings
    valid_settings = ApplicationSettings(
        log_level="INFO",
        cache_ttl_seconds=3600,
    )
    assert valid_settings.log_level == "INFO"
    assert valid_settings.cache_ttl_seconds == 3600

    # Invalid log_level
    with pytest.raises(ValueError):
        ApplicationSettings(
            log_level="INVALID",
            cache_ttl_seconds=3600,
        )

    # Invalid cache_ttl_seconds
    with pytest.raises(ValueError):
        ApplicationSettings(
            log_level="INFO",
            cache_ttl_seconds=0,
        )


def test_settings_validation():
    """Test Settings validation."""
    # Valid settings
    valid_settings = Settings(
        kafka=KafkaSettings(
            bootstrap_servers="localhost:9092",
            input_topic="input-topic",
            output_topic="output-topic",
            group_id="test-group",
        ),
        llm=LLMSettings(
            api_key="test-api-key",
            api_url="https://api.test.com/v1/completions",
            model="test-model",
        ),
        app=ApplicationSettings(
            log_level="INFO",
            cache_ttl_seconds=3600,
        ),
    )
    assert valid_settings.kafka.bootstrap_servers == "localhost:9092"
    assert valid_settings.llm.api_key == "test-api-key"
    assert valid_settings.app.log_level == "INFO"


def test_get_settings(env_vars):
    """Test get_settings function."""
    # Test with environment variables
    settings = get_settings()
    assert settings.kafka.bootstrap_servers == "localhost:9092"
    assert settings.kafka.input_topic == "input-topic"
    assert settings.kafka.output_topic == "output-topic"
    assert settings.kafka.group_id == "test-group"
    assert settings.kafka.auto_offset_reset == "earliest"
    assert settings.kafka.enable_auto_commit is True
    assert settings.llm.api_key == "test-api-key"
    assert str(settings.llm.api_url) == "https://api.test.com/v1/completions"
    assert settings.llm.model == "test-model"
    assert settings.llm.temperature == 0.2
    assert settings.llm.max_tokens == 500
    assert settings.app.log_level == "INFO"
    assert settings.app.cache_ttl_seconds == 3600


def test_get_settings_with_missing_env_vars():
    """Test get_settings function with missing environment variables."""
    # Test with missing environment variables
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            get_settings()
