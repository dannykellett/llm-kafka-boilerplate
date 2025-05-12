"""
Cache module for the LLM-Kafka Boilerplate.

This module provides generic caching functionality.
"""

import logging
import threading
import time
from typing import Any, Dict, Generic, Optional, TypeVar

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for cache value
T = TypeVar("T")


class CacheEntry(Generic[T]):
    """
    Cache entry with timestamp.

    This class represents a cache entry with a value and a timestamp.

    Attributes:
        value: The cached value
        timestamp: The timestamp when the entry was created
    """

    def __init__(self, value: T):
        """
        Initialize the cache entry.

        Args:
            value: The value to cache
        """
        self.value = value
        self.timestamp = time.time()

    def is_expired(self, ttl_seconds: float) -> bool:
        """
        Check if the cache entry is expired.

        Args:
            ttl_seconds: Time-to-live in seconds

        Returns:
            bool: True if the entry is expired, False otherwise
        """
        return time.time() - self.timestamp > ttl_seconds


class Cache(Generic[T]):
    """
    Generic cache with time-based expiration.

    This class provides a thread-safe cache with time-based expiration.

    Attributes:
        ttl_seconds: Time-to-live in seconds
        cache: Dictionary containing cached entries
        lock: Lock for thread-safe access to the cache
    """

    def __init__(self, ttl_seconds: float = 3600):
        """
        Initialize the cache.

        Args:
            ttl_seconds: Time-to-live in seconds (default: 3600)
        """
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, CacheEntry[T]] = {}
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[T]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value, or None if the key is not in the cache or the entry is expired
        """
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                return None

            if entry.is_expired(self.ttl_seconds):
                logger.debug(f"Cache entry for key '{key}' is expired")
                del self.cache[key]
                return None

            logger.debug(f"Cache hit for key '{key}'")
            return entry.value

    def set(self, key: str, value: T) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
        """
        with self.lock:
            logger.debug(f"Caching value for key '{key}'")
            self.cache[key] = CacheEntry(value)

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.

        Args:
            key: The cache key
        """
        with self.lock:
            if key in self.cache:
                logger.debug(f"Deleting cache entry for key '{key}'")
                del self.cache[key]

    def clear(self) -> None:
        """
        Clear the cache.
        """
        with self.lock:
            logger.debug("Clearing cache")
            self.cache.clear()

    def get_or_set(self, key: str, factory: callable) -> T:
        """
        Get a value from the cache, or set it if it's not in the cache.

        Args:
            key: The cache key
            factory: Function to create the value if it's not in the cache

        Returns:
            The cached value
        """
        with self.lock:
            value = self.get(key)
            if value is None:
                logger.debug(f"Cache miss for key '{key}', calling factory")
                value = factory()
                self.set(key, value)
            return value
