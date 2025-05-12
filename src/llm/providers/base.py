"""
Base LLM provider module for the LLM-Kafka Boilerplate.

This module provides the base class for LLM providers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Set up logging
logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""

    pass


class RateLimitError(LLMProviderError):
    """Exception raised when rate limits are exceeded."""

    pass


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    This class defines the interface that all LLM providers must implement.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            str: The generated response.

        Raises:
            LLMProviderError: If there is an error generating the response.
            RateLimitError: If rate limits are exceeded.
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from the last generation.

        Returns:
            Dict[str, Any]: Metrics from the last generation.
        """
        pass
