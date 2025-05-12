"""
Tests for the logging utilities.

This module contains tests for the logging utilities.
"""

import logging
import pytest
from unittest.mock import MagicMock, patch

from src.utils.logging import configure_logging, get_logger


def test_configure_logging_default():
    """Test configure_logging with default parameters."""
    # Mock the root logger
    mock_root_logger = MagicMock(spec=logging.Logger)

    # Mock logging.getLogger to return the mock root logger
    with patch("logging.getLogger", return_value=mock_root_logger) as mock_get_logger:
        # Mock logging.Formatter
        mock_formatter = MagicMock(spec=logging.Formatter)
        with patch(
            "logging.Formatter", return_value=mock_formatter
        ) as mock_formatter_class:
            # Mock logging.StreamHandler
            mock_handler = MagicMock(spec=logging.StreamHandler)
            with patch(
                "logging.StreamHandler", return_value=mock_handler
            ) as mock_handler_class:
                # Call configure_logging
                configure_logging()

                # Verify that getLogger was called with no arguments
                mock_get_logger.assert_called_once_with()

                # Verify that the root logger's level was set to INFO
                mock_root_logger.setLevel.assert_called_once_with(logging.INFO)

                # Verify that the root logger's handlers were removed
                mock_root_logger.removeHandler.assert_not_called()

                # Verify that Formatter was called with the default format
                mock_formatter_class.assert_called_once_with(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )

                # Verify that StreamHandler was called
                mock_handler_class.assert_called_once()

                # Verify that the formatter was set on the handler
                mock_handler.setFormatter.assert_called_once_with(mock_formatter)

                # Verify that the handler was added to the root logger
                mock_root_logger.addHandler.assert_called_once_with(mock_handler)


def test_configure_logging_custom_level():
    """Test configure_logging with custom log level."""
    # Mock the root logger
    mock_root_logger = MagicMock(spec=logging.Logger)

    # Mock logging.getLogger to return the mock root logger
    with patch("logging.getLogger", return_value=mock_root_logger) as mock_get_logger:
        # Call configure_logging with custom log level
        configure_logging(log_level="DEBUG")

        # Verify that the root logger's level was set to DEBUG
        mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)


def test_configure_logging_custom_format():
    """Test configure_logging with custom log format."""
    # Mock the root logger
    mock_root_logger = MagicMock(spec=logging.Logger)

    # Mock logging.getLogger to return the mock root logger
    with patch("logging.getLogger", return_value=mock_root_logger):
        # Mock logging.Formatter
        mock_formatter = MagicMock(spec=logging.Formatter)
        with patch(
            "logging.Formatter", return_value=mock_formatter
        ) as mock_formatter_class:
            # Call configure_logging with custom log format
            custom_format = "%(levelname)s: %(message)s"
            configure_logging(log_format=custom_format)

            # Verify that Formatter was called with the custom format
            mock_formatter_class.assert_called_once_with(custom_format)


def test_configure_logging_with_file():
    """Test configure_logging with log file."""
    # Mock the root logger
    mock_root_logger = MagicMock(spec=logging.Logger)

    # Mock logging.getLogger to return the mock root logger
    with patch("logging.getLogger", return_value=mock_root_logger):
        # Mock logging.FileHandler
        mock_file_handler = MagicMock(spec=logging.FileHandler)
        with patch(
            "logging.FileHandler", return_value=mock_file_handler
        ) as mock_file_handler_class:
            # Mock logging.StreamHandler
            mock_stream_handler = MagicMock(spec=logging.StreamHandler)
            with patch("logging.StreamHandler", return_value=mock_stream_handler):
                # Call configure_logging with log file
                configure_logging(log_file="test.log")

                # Verify that FileHandler was called with the log file
                mock_file_handler_class.assert_called_once_with("test.log")

                # Verify that both handlers were added to the root logger
                assert mock_root_logger.addHandler.call_count == 2


def test_configure_logging_invalid_level():
    """Test configure_logging with invalid log level."""
    with pytest.raises(ValueError):
        configure_logging(log_level="INVALID")


def test_get_logger():
    """Test get_logger function."""
    # Mock logging.getLogger
    mock_logger = MagicMock(spec=logging.Logger)
    with patch("logging.getLogger", return_value=mock_logger) as mock_get_logger:
        # Call get_logger
        logger = get_logger("test_logger")

        # Verify that getLogger was called with the correct name
        mock_get_logger.assert_called_once_with("test_logger")

        # Verify that the logger was returned
        assert logger == mock_logger
