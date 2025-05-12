"""
LLM client module for the LLM-Kafka Boilerplate.

This module provides functionality to interact with LLM services.
It supports different LLM providers and handles error cases, rate limiting, and retries.
"""

import logging
import time
from typing import Any, Dict, Optional, Union

from src.config.config import Settings
from src.llm.providers.base import LLMProvider, LLMProviderError, RateLimitError
from src.llm.providers.openai import OpenAIProvider
from src.llm.providers.openrouter import OpenRouterProvider
from src.llm.rate_limiter import global_rate_limit

# Set up logging
logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory for creating LLM providers.

    This class provides methods for creating LLM providers based on configuration.
    """

    @staticmethod
    def create_provider(settings: Settings) -> LLMProvider:
        """
        Create an LLM provider based on configuration.

        Args:
            settings: Application settings

        Returns:
            LLMProvider: The created LLM provider

        Raises:
            ValueError: If the provider type is not supported
        """
        # Determine provider type based on API URL
        api_url = str(settings.llm.api_url)

        if "openrouter.ai" in api_url:
            logger.info(f"Creating OpenRouter provider with model {settings.llm.model}")
            return OpenRouterProvider(
                api_key=settings.llm.api_key,
                api_url=api_url,
                model=settings.llm.model,
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens,
            )
        elif "openai.com" in api_url:
            logger.info(f"Creating OpenAI provider with model {settings.llm.model}")
            return OpenAIProvider(
                api_key=settings.llm.api_key,
                api_url=api_url,
                model=settings.llm.model,
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens,
            )
        else:
            # Default to OpenAI provider
            logger.warning(f"Unknown API URL: {api_url}, defaulting to OpenAI provider")
            return OpenAIProvider(
                api_key=settings.llm.api_key,
                api_url=api_url,
                model=settings.llm.model,
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.max_tokens,
            )


class LLMClient:
    """
    Client for interacting with LLM services.

    This class provides methods for generating text using LLM services.
    It handles provider selection, error handling, rate limiting, and retries.

    Attributes:
        settings: Application settings
        provider: LLM provider
        max_retries: Maximum number of retries for API calls
        retry_delay: Delay between retries in seconds
    """

    def __init__(
        self,
        settings: Settings,
        provider: Optional[LLMProvider] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        """
        Initialize the LLM client.

        Args:
            settings: Application settings
            provider: LLM provider (if None, one will be created based on settings)
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
        """
        self.settings = settings
        self.provider = provider or LLMProviderFactory.create_provider(settings)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)

    def generate(self, prompt: str) -> str:
        """
        Generate text using the LLM provider.

        This method handles rate limiting and retries.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            str: The generated text

        Raises:
            LLMProviderError: If there is an error generating the text after retries
        """
        retries = 0
        last_error = None

        while retries <= self.max_retries:
            try:
                # Apply global rate limiting
                global_wait = global_rate_limit(min_delay_seconds=60)
                if global_wait > 0:
                    self.logger.info(
                        f"Applied global rate limit, waited {global_wait:.2f} seconds"
                    )

                # Generate text
                start_time = time.time()
                response = self.provider.generate(prompt)
                generation_time = time.time() - start_time

                self.logger.info(
                    f"Generated text in {generation_time:.2f} seconds (retries: {retries})"
                )

                # Return the generated text
                return response

            except RateLimitError as e:
                self.logger.warning(
                    f"Rate limit exceeded (retry {retries}/{self.max_retries}): {e}"
                )
                last_error = e
                retries += 1

                # Exponential backoff for rate limit errors
                wait_time = self.retry_delay * (2**retries)
                self.logger.info(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)

            except LLMProviderError as e:
                self.logger.error(
                    f"Provider error (retry {retries}/{self.max_retries}): {e}"
                )
                last_error = e
                retries += 1

                # Linear backoff for other errors
                wait_time = self.retry_delay
                self.logger.info(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)

        # If we've exhausted retries, raise the last error
        if last_error:
            raise last_error

        # This should never happen, but just in case
        raise LLMProviderError("Failed to generate text after retries")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from the last generation.

        Returns:
            Dict[str, Any]: Metrics from the last generation
        """
        return self.provider.get_metrics()
