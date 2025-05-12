"""
Configuration module for the LLM-Kafka Boilerplate.

This module provides configuration settings for the application using Pydantic for validation.
"""

from src.config.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]
