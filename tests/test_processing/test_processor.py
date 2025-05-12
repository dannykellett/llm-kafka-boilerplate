"""
Tests for the processor module.

This module contains tests for the processor functionality.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.processing.processor import Processor, ProcessingError


class TestProcessor(Processor):
    """Test implementation of the Processor abstract class."""

    def process(self, message):
        """Process a message."""
        if message.get("fail"):
            raise ProcessingError("Test failure")
        processed_message = message.copy()
        processed_message["processed"] = True
        return processed_message


def test_processor_initialization(mock_settings, mock_llm_client):
    """Test processor initialization."""
    processor = TestProcessor(mock_settings, mock_llm_client)
    assert processor.settings == mock_settings
    assert processor.llm_client == mock_llm_client


def test_processor_validate_message():
    """Test processor validate_message method."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Default implementation should not raise an exception
    message = {"id": "test-id", "content": "Test content"}
    processor.validate_message(message)


def test_processor_preprocess():
    """Test processor preprocess method."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Default implementation should return the message unchanged
    message = {"id": "test-id", "content": "Test content"}
    preprocessed_message = processor.preprocess(message)
    assert preprocessed_message == message


def test_processor_process():
    """Test processor process method."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Test successful processing
    message = {"id": "test-id", "content": "Test content"}
    processed_message = processor.process(message)
    assert processed_message["processed"] is True

    # Test processing failure
    message = {"id": "test-id", "content": "Test content", "fail": True}
    with pytest.raises(ProcessingError):
        processor.process(message)


def test_processor_postprocess():
    """Test processor postprocess method."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Default implementation should return the message unchanged
    message = {"id": "test-id", "content": "Test content", "processed": True}
    postprocessed_message = processor.postprocess(message)
    assert postprocessed_message == message


def test_processor_handle():
    """Test processor handle method."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Test successful handling
    message = {"id": "test-id", "content": "Test content"}
    result = processor.handle(message)
    assert result["processed"] is True

    # Test handling failure
    message = {"id": "test-id", "content": "Test content", "fail": True}
    with pytest.raises(ProcessingError):
        processor.handle(message)


def test_processor_handle_with_validation_error():
    """Test processor handle method with validation error."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Mock validate_message to raise an exception
    processor.validate_message = MagicMock(
        side_effect=ProcessingError("Validation error")
    )

    message = {"id": "test-id", "content": "Test content"}
    with pytest.raises(ProcessingError):
        processor.handle(message)


def test_processor_handle_with_preprocess_error():
    """Test processor handle method with preprocess error."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Mock preprocess to raise an exception
    processor.preprocess = MagicMock(side_effect=ProcessingError("Preprocess error"))

    message = {"id": "test-id", "content": "Test content"}
    with pytest.raises(ProcessingError):
        processor.handle(message)


def test_processor_handle_with_postprocess_error():
    """Test processor handle method with postprocess error."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Mock postprocess to raise an exception
    processor.postprocess = MagicMock(side_effect=ProcessingError("Postprocess error"))

    message = {"id": "test-id", "content": "Test content"}
    with pytest.raises(ProcessingError):
        processor.handle(message)


def test_processor_handle_with_unexpected_error():
    """Test processor handle method with unexpected error."""
    processor = TestProcessor(MagicMock(), MagicMock())

    # Mock process to raise an unexpected exception
    processor.process = MagicMock(side_effect=ValueError("Unexpected error"))

    message = {"id": "test-id", "content": "Test content"}
    with pytest.raises(ProcessingError):
        processor.handle(message)
