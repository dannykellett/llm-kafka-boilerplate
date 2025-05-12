"""
Tests for the examples manager module.

This module contains tests for the examples manager functionality.
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from src.data.examples_manager import ExamplesManager


def test_examples_manager_initialization(mock_settings):
    """Test ExamplesManager initialization."""
    loader_func = MagicMock(return_value={"examples": []})
    manager = ExamplesManager(mock_settings, loader_func)

    assert manager.config == mock_settings
    assert manager.refresh_interval_seconds == mock_settings.app.cache_ttl_seconds
    assert manager._should_refresh is False
    assert manager.refresh_thread is None
    assert manager._loader_func == loader_func


def test_get_examples(mock_settings):
    """Test get_examples method."""
    # Create a mock loader function
    examples_data = {"examples": [{"id": 1, "text": "Example 1"}]}
    loader_func = MagicMock(return_value=examples_data)

    # Create the manager
    manager = ExamplesManager(mock_settings, loader_func)

    # Get examples
    examples = manager.get_examples()

    # Verify that the loader function was called
    loader_func.assert_called_once()

    # Verify that the examples were returned
    assert examples == examples_data

    # Reset the mock
    loader_func.reset_mock()

    # Get examples again (should use cache)
    examples = manager.get_examples()

    # Verify that the loader function was not called again
    loader_func.assert_not_called()

    # Verify that the examples were returned
    assert examples == examples_data


def test_get_examples_cache_expiration(mock_settings):
    """Test get_examples method with cache expiration."""
    # Create a mock loader function
    examples_data_1 = {"examples": [{"id": 1, "text": "Example 1"}]}
    examples_data_2 = {"examples": [{"id": 2, "text": "Example 2"}]}

    loader_func = MagicMock(side_effect=[examples_data_1, examples_data_2])

    # Create the manager with a short TTL
    mock_settings.app.cache_ttl_seconds = 1
    manager = ExamplesManager(mock_settings, loader_func)

    # Get examples
    examples = manager.get_examples()

    # Verify that the loader function was called
    loader_func.assert_called_once()

    # Verify that the examples were returned
    assert examples == examples_data_1

    # Reset the mock
    loader_func.reset_mock()

    # Sleep to ensure the cache expires
    time.sleep(1.1)

    # Get examples again (should reload)
    examples = manager.get_examples()

    # Verify that the loader function was called again
    loader_func.assert_called_once()

    # Verify that the new examples were returned
    assert examples == examples_data_2


def test_start_background_refresh(mock_settings):
    """Test start_background_refresh method."""
    loader_func = MagicMock(return_value={"examples": []})
    manager = ExamplesManager(mock_settings, loader_func)

    # Start background refresh
    with patch.object(manager, "_background_refresh_worker") as mock_worker:
        manager.start_background_refresh()

        # Verify that the thread was started
        assert manager._should_refresh is True
        assert manager.refresh_thread is not None
        assert manager.refresh_thread.daemon is True

        # Verify that starting again does nothing
        manager.start_background_refresh()

        # Stop background refresh
        manager.stop_background_refresh()

        # Verify that the thread was stopped
        assert manager._should_refresh is False
        assert manager.refresh_thread is None


def test_stop_background_refresh_when_not_running(mock_settings):
    """Test stop_background_refresh method when not running."""
    loader_func = MagicMock(return_value={"examples": []})
    manager = ExamplesManager(mock_settings, loader_func)

    # Stop background refresh when not running
    manager.stop_background_refresh()

    # Verify that nothing happened
    assert manager._should_refresh is False
    assert manager.refresh_thread is None


def test_background_refresh_worker(mock_settings):
    """Test _background_refresh_worker method."""
    # Create a mock loader function
    examples_data = {"examples": [{"id": 1, "text": "Example 1"}]}
    loader_func = MagicMock(return_value=examples_data)

    # Create the manager with a short refresh interval
    mock_settings.app.cache_ttl_seconds = 1
    manager = ExamplesManager(mock_settings, loader_func)

    # Mock time.sleep to avoid waiting
    with patch("time.sleep") as mock_sleep:
        # Set up the manager for background refresh
        manager._should_refresh = True

        # Call the worker directly (simulating the thread)
        manager._background_refresh_worker()

        # Verify that the loader function was called
        loader_func.assert_called_once()

        # Verify that sleep was called with the refresh interval
        mock_sleep.assert_called_with(manager.refresh_interval_seconds)


def test_background_refresh_worker_with_exception(mock_settings):
    """Test _background_refresh_worker method with exception."""
    # Create a mock loader function that raises an exception
    loader_func = MagicMock(side_effect=Exception("Test exception"))

    # Create the manager with a short refresh interval
    mock_settings.app.cache_ttl_seconds = 1
    manager = ExamplesManager(mock_settings, loader_func)

    # Mock time.sleep to avoid waiting
    with patch("time.sleep") as mock_sleep:
        # Set up the manager for background refresh
        manager._should_refresh = True

        # Call the worker directly (simulating the thread)
        manager._background_refresh_worker()

        # Verify that the loader function was called
        loader_func.assert_called_once()

        # Verify that sleep was called with the refresh interval
        mock_sleep.assert_called_with(manager.refresh_interval_seconds)


def test_background_refresh_worker_stops_when_should_refresh_is_false(mock_settings):
    """Test _background_refresh_worker method stops when _should_refresh is False."""
    loader_func = MagicMock(return_value={"examples": []})
    manager = ExamplesManager(mock_settings, loader_func)

    # Mock time.sleep to set _should_refresh to False after first iteration
    def sleep_side_effect(seconds):
        manager._should_refresh = False

    with patch("time.sleep", side_effect=sleep_side_effect):
        # Set up the manager for background refresh
        manager._should_refresh = True

        # Call the worker directly (simulating the thread)
        manager._background_refresh_worker()

        # Verify that the loader function was called once
        loader_func.assert_called_once()
