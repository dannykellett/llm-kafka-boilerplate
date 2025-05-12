"""
Tests for the error handling utilities.

This module contains tests for the error handling utilities.
"""

import logging
import pytest
from unittest.mock import MagicMock, patch

from src.utils.error_handling import handle_exception, retry


def test_handle_exception():
    """Test handle_exception function."""
    # Create a mock logger
    mock_logger = MagicMock(spec=logging.Logger)

    # Create an exception
    exception = ValueError("Test error")

    # Test with raise_exception=False
    handle_exception(
        exception=exception,
        error_message="Test error message",
        logger=mock_logger,
        raise_exception=False,
    )

    # Verify that the logger was called
    mock_logger.error.assert_called_once_with("Test error message: Test error")

    # Test with raise_exception=True
    with pytest.raises(ValueError) as excinfo:
        handle_exception(
            exception=exception,
            error_message="Test error message",
            logger=mock_logger,
            raise_exception=True,
        )

    # Verify that the exception was raised
    assert str(excinfo.value) == "Test error message: Test error"

    # Test with custom exception type
    with pytest.raises(RuntimeError) as excinfo:
        handle_exception(
            exception=exception,
            error_message="Test error message",
            logger=mock_logger,
            raise_exception=True,
            exception_type=RuntimeError,
        )

    # Verify that the exception was raised with the custom type
    assert isinstance(excinfo.value, RuntimeError)
    assert str(excinfo.value) == "Test error message: Test error"


def test_retry_decorator_success():
    """Test retry decorator with successful function."""
    # Create a mock function that succeeds
    mock_func = MagicMock(return_value="success")

    # Apply the retry decorator
    decorated_func = retry()(mock_func)

    # Call the decorated function
    result = decorated_func("arg1", "arg2", kwarg1="kwarg1")

    # Verify that the function was called once
    mock_func.assert_called_once_with("arg1", "arg2", kwarg1="kwarg1")

    # Verify that the result is correct
    assert result == "success"


def test_retry_decorator_failure():
    """Test retry decorator with failing function."""
    # Create a mock function that fails
    mock_func = MagicMock(side_effect=ValueError("Test error"))

    # Apply the retry decorator
    decorated_func = retry(max_retries=2, retry_delay=0.01)(mock_func)

    # Call the decorated function
    with pytest.raises(ValueError) as excinfo:
        decorated_func()

    # Verify that the function was called 3 times (initial + 2 retries)
    assert mock_func.call_count == 3

    # Verify that the exception was raised
    assert str(excinfo.value) == "Test error"


def test_retry_decorator_eventual_success():
    """Test retry decorator with function that eventually succeeds."""
    # Create a mock function that fails twice then succeeds
    mock_func = MagicMock(
        side_effect=[ValueError("Test error"), ValueError("Test error"), "success"]
    )

    # Apply the retry decorator
    decorated_func = retry(max_retries=2, retry_delay=0.01)(mock_func)

    # Call the decorated function
    result = decorated_func()

    # Verify that the function was called 3 times (initial + 2 retries)
    assert mock_func.call_count == 3

    # Verify that the result is correct
    assert result == "success"


def test_retry_decorator_with_specific_exceptions():
    """Test retry decorator with specific exceptions."""
    # Create a mock function that raises different exceptions
    mock_func = MagicMock(
        side_effect=[ValueError("Test error"), RuntimeError("Runtime error"), "success"]
    )

    # Apply the retry decorator with specific exceptions
    decorated_func = retry(max_retries=2, retry_delay=0.01, exceptions=[ValueError])(
        mock_func
    )

    # Call the decorated function
    with pytest.raises(RuntimeError) as excinfo:
        decorated_func()

    # Verify that the function was called 2 times (initial + 1 retry)
    assert mock_func.call_count == 2

    # Verify that the exception was raised
    assert str(excinfo.value) == "Runtime error"


def test_retry_decorator_with_backoff():
    """Test retry decorator with backoff."""
    # Create a mock function that always fails
    mock_func = MagicMock(side_effect=ValueError("Test error"))

    # Mock time.sleep
    with patch("time.sleep") as mock_sleep:
        # Apply the retry decorator with backoff
        decorated_func = retry(max_retries=2, retry_delay=1.0, backoff_factor=2.0)(
            mock_func
        )

        # Call the decorated function
        with pytest.raises(ValueError):
            decorated_func()

        # Verify that sleep was called with increasing delays
        mock_sleep.assert_any_call(1.0)  # First retry
        mock_sleep.assert_any_call(2.0)  # Second retry (with backoff)
