"""
Data module for the LLM-Kafka Boilerplate.

This module provides functionality for data management, including caching
and examples management.
"""

from src.data.cache import Cache, CacheEntry
from src.data.examples_manager import ExamplesManager

__all__ = ["Cache", "CacheEntry", "ExamplesManager"]
