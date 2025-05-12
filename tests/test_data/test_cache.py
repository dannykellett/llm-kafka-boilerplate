"""
Tests for the cache module.

This module contains tests for the cache functionality.
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from src.data.cache import Cache, CacheEntry


def test_cache_entry_initialization():
    """Test CacheEntry initialization."""
    value = "test_value"
    entry = CacheEntry(value)
    assert entry.value == value
    assert entry.timestamp <= time.time()


def test_cache_entry_is_expired():
    """Test CacheEntry is_expired method."""
    entry = CacheEntry("test_value")

    # Entry should not be expired immediately
    assert not entry.is_expired(ttl_seconds=3600)

    # Entry should be expired if ttl is 0
    assert entry.is_expired(ttl_seconds=0)

    # Entry should be expired if ttl is negative
    assert entry.is_expired(ttl_seconds=-1)

    # Entry should be expired after ttl
    with patch.object(time, "time", return_value=entry.timestamp + 3601):
        assert entry.is_expired(ttl_seconds=3600)


def test_cache_initialization():
    """Test Cache initialization."""
    cache = Cache()
    assert cache.ttl_seconds == 3600
    assert cache.cache == {}

    cache = Cache(ttl_seconds=1800)
    assert cache.ttl_seconds == 1800


def test_cache_get_nonexistent_key():
    """Test Cache get method with nonexistent key."""
    cache = Cache()
    assert cache.get("nonexistent") is None


def test_cache_get_expired_key():
    """Test Cache get method with expired key."""
    cache = Cache(ttl_seconds=1)
    cache.set("key", "value")

    # Sleep to ensure the entry expires
    time.sleep(1.1)

    assert cache.get("key") is None
    assert "key" not in cache.cache


def test_cache_get_valid_key():
    """Test Cache get method with valid key."""
    cache = Cache()
    cache.set("key", "value")
    assert cache.get("key") == "value"


def test_cache_set():
    """Test Cache set method."""
    cache = Cache()
    cache.set("key", "value")
    assert "key" in cache.cache
    assert cache.cache["key"].value == "value"


def test_cache_delete():
    """Test Cache delete method."""
    cache = Cache()
    cache.set("key", "value")
    assert "key" in cache.cache

    cache.delete("key")
    assert "key" not in cache.cache

    # Deleting a nonexistent key should not raise an exception
    cache.delete("nonexistent")


def test_cache_clear():
    """Test Cache clear method."""
    cache = Cache()
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert len(cache.cache) == 2

    cache.clear()
    assert len(cache.cache) == 0


def test_cache_get_or_set_with_existing_key():
    """Test Cache get_or_set method with existing key."""
    cache = Cache()
    cache.set("key", "value")

    factory = MagicMock(return_value="new_value")
    result = cache.get_or_set("key", factory)

    assert result == "value"
    factory.assert_not_called()


def test_cache_get_or_set_with_nonexistent_key():
    """Test Cache get_or_set method with nonexistent key."""
    cache = Cache()

    factory = MagicMock(return_value="new_value")
    result = cache.get_or_set("key", factory)

    assert result == "new_value"
    factory.assert_called_once()
    assert cache.get("key") == "new_value"


def test_cache_get_or_set_with_expired_key():
    """Test Cache get_or_set method with expired key."""
    cache = Cache(ttl_seconds=1)
    cache.set("key", "value")

    # Sleep to ensure the entry expires
    time.sleep(1.1)

    factory = MagicMock(return_value="new_value")
    result = cache.get_or_set("key", factory)

    assert result == "new_value"
    factory.assert_called_once()
    assert cache.get("key") == "new_value"


def test_cache_thread_safety():
    """Test Cache thread safety."""
    # This is a basic test that doesn't actually test thread safety,
    # but at least ensures that the lock is acquired and released properly
    cache = Cache()

    with cache._lock:
        cache.set("key", "value")
        assert cache.get("key") == "value"
