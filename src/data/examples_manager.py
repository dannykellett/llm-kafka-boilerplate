"""
Examples manager module for the LLM-Kafka Boilerplate.

This module provides functionality for managing examples with background refresh.
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Callable

from src.config.config import Settings
from src.data.cache import Cache

# Set up logging
logger = logging.getLogger(__name__)


class ExamplesManager:
    """
    Manager for examples.

    This class is responsible for caching and providing access to
    examples. It supports:
    - Loading examples from a data source
    - Caching examples in memory
    - Periodically refreshing examples in the background
    - Thread-safe access to examples

    Attributes:
        config: The application configuration.
        cache: Cache for examples.
        refresh_thread: Thread for background refresh of examples.
        refresh_interval_seconds: Interval for refreshing examples in seconds.
        _should_refresh: Flag to control background refresh thread.
        _lock: Lock for thread-safe access to the cache.
        _loader_func: Function to load examples.
    """

    def __init__(self, config: Settings, loader_func: Callable[[], Dict[str, Any]]):
        """
        Initialize the examples manager.

        Args:
            config: The application configuration.
            loader_func: Function to load examples.
        """
        self.config = config
        self.cache = Cache(ttl_seconds=config.app.cache_ttl_seconds)
        self.refresh_thread: Optional[threading.Thread] = None
        self.refresh_interval_seconds = config.app.cache_ttl_seconds
        self._should_refresh = False
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._loader_func = loader_func

        # Configure logging
        self.logger = logging.getLogger(__name__)

    def get_examples(self) -> Dict[str, Any]:
        """
        Get the examples.

        This method returns the cached examples if they are still valid,
        otherwise it loads new examples using the loader function.

        Returns:
            Dict[str, Any]: The examples.
        """
        return self.cache.get_or_set("examples", self._loader_func)

    def start_background_refresh(self) -> None:
        """
        Start background refresh of examples.

        This method starts a background thread that periodically refreshes
        the examples using the loader function.
        """
        with self._lock:
            if self.refresh_thread is not None:
                self.logger.warning("Background refresh already running")
                return

            self._should_refresh = True
            self.refresh_thread = threading.Thread(
                target=self._background_refresh_worker,
                daemon=True,  # Daemon thread will exit when main thread exits
            )
            self.refresh_thread.start()
            self.logger.info(
                f"Started background refresh thread with interval {self.refresh_interval_seconds} seconds"
            )

    def stop_background_refresh(self) -> None:
        """
        Stop background refresh of examples.

        This method stops the background refresh thread.
        """
        with self._lock:
            if self.refresh_thread is None:
                self.logger.warning("No background refresh running")
                return

            self._should_refresh = False
            self.refresh_thread = None
            self.logger.info("Stopped background refresh thread")

    def _background_refresh_worker(self) -> None:
        """
        Background worker for refreshing examples.

        This method runs in a background thread and periodically refreshes
        the examples using the loader function.
        """
        while self._should_refresh:
            try:
                # Load examples using the loader function
                self.logger.info("Background refresh: Loading examples")
                examples = self._loader_func()

                # Update cache
                with self._lock:
                    self.cache.set("examples", examples)
                    self.logger.info("Background refresh: Updated examples cache")

                # Sleep after refresh
                time.sleep(self.refresh_interval_seconds)

                # Check if we should still refresh
                if not self._should_refresh:
                    break

            except Exception as e:
                self.logger.error(f"Error in background refresh: {e}")
                # Sleep before trying again
                time.sleep(self.refresh_interval_seconds)
