"""
Metrics utilities for the LLM-Kafka Boilerplate.

This module provides utilities for collecting and reporting metrics.
"""

import logging
import time
from typing import Any, Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collector for application metrics.

    This class provides methods for collecting and reporting metrics.

    Attributes:
        metrics: Dictionary of collected metrics
    """

    def __init__(self):
        """
        Initialize the metrics collector.
        """
        self.metrics: Dict[str, Any] = {}
        self.timers: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)

    def record_metric(self, name: str, value: Any) -> None:
        """
        Record a metric.

        Args:
            name: Metric name
            value: Metric value
        """
        self.metrics[name] = value
        self.logger.debug(f"Recorded metric: {name}={value}")

    def increment_counter(self, name: str, increment: int = 1) -> int:
        """
        Increment a counter metric.

        Args:
            name: Counter name
            increment: Increment value (default: 1)

        Returns:
            int: New counter value
        """
        current_value = self.metrics.get(name, 0)
        new_value = current_value + increment
        self.metrics[name] = new_value
        self.logger.debug(f"Incremented counter: {name}={new_value}")
        return new_value

    def start_timer(self, name: str) -> None:
        """
        Start a timer.

        Args:
            name: Timer name
        """
        self.timers[name] = time.time()
        self.logger.debug(f"Started timer: {name}")

    def stop_timer(self, name: str) -> Optional[float]:
        """
        Stop a timer and record the elapsed time.

        Args:
            name: Timer name

        Returns:
            float: Elapsed time in seconds, or None if the timer was not started
        """
        if name not in self.timers:
            self.logger.warning(f"Timer not started: {name}")
            return None

        start_time = self.timers.pop(name)
        elapsed_time = time.time() - start_time
        self.record_metric(f"{name}_seconds", elapsed_time)
        self.logger.debug(f"Stopped timer: {name}={elapsed_time:.3f}s")
        return elapsed_time

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.

        Returns:
            Dict[str, Any]: Dictionary of collected metrics
        """
        return self.metrics.copy()

    def reset(self) -> None:
        """
        Reset all metrics.
        """
        self.metrics.clear()
        self.timers.clear()
        self.logger.debug("Reset metrics")

    def report_metrics(self) -> None:
        """
        Report all collected metrics.
        """
        self.logger.info(f"Metrics: {self.metrics}")
