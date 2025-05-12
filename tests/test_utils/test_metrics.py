"""
Tests for the metrics utilities.

This module contains tests for the metrics utilities.
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from src.utils.metrics import MetricsCollector


def test_metrics_collector_initialization():
    """Test MetricsCollector initialization."""
    collector = MetricsCollector()
    assert collector.metrics == {}
    assert collector.timers == {}


def test_record_metric():
    """Test record_metric method."""
    collector = MetricsCollector()

    # Record a metric
    collector.record_metric("test_metric", 42)
    assert collector.metrics["test_metric"] == 42

    # Record another metric
    collector.record_metric("another_metric", "value")
    assert collector.metrics["another_metric"] == "value"

    # Override a metric
    collector.record_metric("test_metric", 43)
    assert collector.metrics["test_metric"] == 43


def test_increment_counter():
    """Test increment_counter method."""
    collector = MetricsCollector()

    # Increment a counter that doesn't exist
    result = collector.increment_counter("test_counter")
    assert result == 1
    assert collector.metrics["test_counter"] == 1

    # Increment the counter again
    result = collector.increment_counter("test_counter")
    assert result == 2
    assert collector.metrics["test_counter"] == 2

    # Increment with a custom value
    result = collector.increment_counter("test_counter", 5)
    assert result == 7
    assert collector.metrics["test_counter"] == 7


def test_start_timer():
    """Test start_timer method."""
    collector = MetricsCollector()

    # Start a timer
    collector.start_timer("test_timer")
    assert "test_timer" in collector.timers
    assert collector.timers["test_timer"] <= time.time()


def test_stop_timer():
    """Test stop_timer method."""
    collector = MetricsCollector()

    # Start a timer
    collector.start_timer("test_timer")

    # Sleep a bit to ensure the timer has a non-zero value
    time.sleep(0.01)

    # Stop the timer
    elapsed_time = collector.stop_timer("test_timer")

    # Verify that the timer was stopped
    assert "test_timer" not in collector.timers

    # Verify that the elapsed time was recorded
    assert collector.metrics["test_timer_seconds"] == elapsed_time

    # Verify that the elapsed time is reasonable
    assert elapsed_time >= 0.01


def test_stop_timer_not_started():
    """Test stop_timer method with a timer that wasn't started."""
    collector = MetricsCollector()

    # Stop a timer that wasn't started
    elapsed_time = collector.stop_timer("nonexistent_timer")

    # Verify that the result is None
    assert elapsed_time is None

    # Verify that no metric was recorded
    assert "nonexistent_timer_seconds" not in collector.metrics


def test_get_metrics():
    """Test get_metrics method."""
    collector = MetricsCollector()

    # Record some metrics
    collector.record_metric("test_metric", 42)
    collector.record_metric("another_metric", "value")

    # Get metrics
    metrics = collector.get_metrics()

    # Verify that the metrics were returned
    assert metrics == {"test_metric": 42, "another_metric": "value"}

    # Verify that the returned metrics are a copy
    metrics["new_metric"] = "new_value"
    assert "new_metric" not in collector.metrics


def test_reset():
    """Test reset method."""
    collector = MetricsCollector()

    # Record some metrics
    collector.record_metric("test_metric", 42)
    collector.start_timer("test_timer")

    # Reset
    collector.reset()

    # Verify that metrics were reset
    assert collector.metrics == {}
    assert collector.timers == {}


def test_report_metrics():
    """Test report_metrics method."""
    collector = MetricsCollector()

    # Record some metrics
    collector.record_metric("test_metric", 42)
    collector.record_metric("another_metric", "value")

    # Mock the logger
    collector.logger = MagicMock()

    # Report metrics
    collector.report_metrics()

    # Verify that the logger was called
    collector.logger.info.assert_called_once_with(
        "Metrics: {'test_metric': 42, 'another_metric': 'value'}"
    )
