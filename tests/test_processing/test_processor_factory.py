"""
Tests for the processor factory module.

This module contains tests for the processor factory functionality.
"""

import pytest
from unittest.mock import MagicMock

from src.processing.processor import Processor, ProcessingError
from src.processing.processor_factory import ProcessorFactory


class TestProcessor(Processor):
    """Test implementation of the Processor abstract class."""

    def process(self, message):
        """Process a message."""
        processed_message = message.copy()
        processed_message["processed"] = True
        return processed_message


class AnotherTestProcessor(Processor):
    """Another test implementation of the Processor abstract class."""

    def process(self, message):
        """Process a message."""
        processed_message = message.copy()
        processed_message["processed_by"] = "another"
        return processed_message


def test_processor_factory_initialization(mock_settings, mock_llm_client):
    """Test processor factory initialization."""
    factory = ProcessorFactory(mock_settings, mock_llm_client)
    assert factory.settings == mock_settings
    assert factory.llm_client == mock_llm_client
    assert factory.processors == {}


def test_register_processor(mock_processor_factory):
    """Test register_processor method."""
    # Register a processor
    mock_processor_factory.register_processor("test", TestProcessor)
    assert "test" in mock_processor_factory.processors
    assert mock_processor_factory.processors["test"] == TestProcessor

    # Register another processor
    mock_processor_factory.register_processor("another", AnotherTestProcessor)
    assert "another" in mock_processor_factory.processors
    assert mock_processor_factory.processors["another"] == AnotherTestProcessor

    # Override a processor
    mock_processor_factory.register_processor("test", AnotherTestProcessor)
    assert mock_processor_factory.processors["test"] == AnotherTestProcessor


def test_create_processor(mock_processor_factory):
    """Test create_processor method."""
    # Register processors
    mock_processor_factory.register_processor("test", TestProcessor)
    mock_processor_factory.register_processor("another", AnotherTestProcessor)

    # Create a processor
    processor = mock_processor_factory.create_processor("test")
    assert isinstance(processor, TestProcessor)

    # Create another processor
    processor = mock_processor_factory.create_processor("another")
    assert isinstance(processor, AnotherTestProcessor)

    # Try to create a processor that doesn't exist
    with pytest.raises(ProcessingError):
        mock_processor_factory.create_processor("nonexistent")


def test_get_registered_processors(mock_processor_factory):
    """Test get_registered_processors method."""
    # Register processors
    mock_processor_factory.register_processor("test", TestProcessor)
    mock_processor_factory.register_processor("another", AnotherTestProcessor)

    # Get registered processors
    processors = mock_processor_factory.get_registered_processors()
    assert "test" in processors
    assert processors["test"] == TestProcessor
    assert "another" in processors
    assert processors["another"] == AnotherTestProcessor

    # Verify that the returned dictionary is a copy
    processors["new"] = MagicMock()
    assert "new" not in mock_processor_factory.processors


def test_processor_creation_with_dependencies(mock_settings, mock_llm_client):
    """Test that processors are created with the correct dependencies."""
    factory = ProcessorFactory(mock_settings, mock_llm_client)
    factory.register_processor("test", TestProcessor)

    # Create a processor
    processor = factory.create_processor("test")

    # Verify that the processor has the correct dependencies
    assert processor.settings == mock_settings
    assert processor.llm_client == mock_llm_client
