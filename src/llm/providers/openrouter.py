"""
OpenRouter LLM provider module for the LLM-Kafka Boilerplate.

This module provides an implementation of the LLMProvider interface for OpenRouter.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

import requests

from src.llm.providers.base import LLMProvider, LLMProviderError, RateLimitError

# Set up logging
logger = logging.getLogger(__name__)


class OpenRouterRateLimitError(RateLimitError):
    """Exception raised when OpenRouter rate limits are exceeded."""

    def __init__(
        self, message: str, limit_remaining: float, rate_limit: Dict[str, Any]
    ):
        """
        Initialize the OpenRouter rate limit error.

        Args:
            message: Error message.
            limit_remaining: Remaining monetary limit.
            rate_limit: Rate limit information (requests and interval).
        """
        super().__init__(message)
        self.limit_remaining = limit_remaining
        self.rate_limit = rate_limit


class OpenRouterProvider(LLMProvider):
    """
    OpenRouter LLM provider implementation.

    This class implements the LLMProvider interface for OpenRouter.

    Attributes:
        api_key: API key for the OpenRouter service.
        api_url: URL for the OpenRouter service API.
        model: Model to use for generation.
        temperature: Temperature parameter for generation.
        max_tokens: Maximum number of tokens to generate.
        timeout: Timeout for API requests in seconds.
        metrics: Metrics from the last generation.
        openrouter_limits: Current OpenRouter usage limits.
    """

    def __init__(
        self,
        api_key: str,
        api_url: str,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 500,
        timeout: int = 30,
    ):
        """
        Initialize the OpenRouter provider.

        Args:
            api_key: API key for the OpenRouter service.
            api_url: URL for the OpenRouter service API.
            model: Model to use for generation.
            temperature: Temperature parameter for generation.
            max_tokens: Maximum number of tokens to generate.
            timeout: Timeout for API requests in seconds.
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.metrics: Dict[str, Any] = {}
        self.openrouter_limits: Optional[Dict[str, Any]] = None
        self.logger = logging.getLogger(__name__)

    def generate(self, prompt: str) -> str:
        """
        Generate a response using the OpenRouter API.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            str: The generated response.

        Raises:
            LLMProviderError: If there is an error generating the response.
            RateLimitError: If rate limits are exceeded.
            OpenRouterRateLimitError: If OpenRouter rate limits are exceeded.
        """
        # First, check if we have limits and need to wait
        if self.openrouter_limits:
            self._check_openrouter_limits()

        try:
            self.logger.debug(f"Sending request to OpenRouter API: {self.api_url}")

            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "llm-kafka-boilerplate",  # Identify your application
                "X-Title": "LLM-Kafka Boilerplate",  # Identify your application
            }

            # Send the request
            start_time = time.time()
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response_time = time.time() - start_time

            # Check for errors
            response.raise_for_status()

            # Parse the response
            response_data = response.json()

            # Extract the generated text
            if "choices" in response_data and len(response_data["choices"]) > 0:
                generated_text = response_data["choices"][0]["message"]["content"]
            else:
                raise LLMProviderError("No choices in OpenRouter response")

            # Store metrics
            self.metrics = {
                "token_usage": response_data.get("usage", {}),
                "model_info": response_data.get("model", self.model),
                "response_time": response_time,
                "status_code": response.status_code,
            }

            # After successful generation, fetch current OpenRouter limits
            try:
                self._fetch_openrouter_limits()
            except Exception as e:
                # Log but don't fail the request if we can't fetch limits
                self.logger.warning(f"Failed to fetch OpenRouter limits: {e}")

            return generated_text

        except requests.exceptions.HTTPError as e:
            # Check for rate limit error
            if e.response.status_code == 429:
                self.logger.warning(f"OpenRouter rate limit exceeded: {e}")
                raise RateLimitError(f"OpenRouter rate limit exceeded: {e}")

            self.logger.error(f"HTTP error from OpenRouter API: {e}")
            raise LLMProviderError(f"HTTP error from OpenRouter API: {e}")

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error to OpenRouter API: {e}")
            raise LLMProviderError(f"Connection error to OpenRouter API: {e}")

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout connecting to OpenRouter API: {e}")
            raise LLMProviderError(f"Timeout connecting to OpenRouter API: {e}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from OpenRouter API: {e}")
            raise LLMProviderError(f"Invalid JSON response from OpenRouter API: {e}")

        except Exception as e:
            self.logger.error(f"Unexpected error with OpenRouter API: {e}")
            raise LLMProviderError(f"Unexpected error with OpenRouter API: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from the last generation.

        Returns:
            Dict[str, Any]: Metrics from the last generation.
        """
        return self.metrics

    def _fetch_openrouter_limits(self) -> None:
        """
        Fetch current OpenRouter usage limits.

        Makes a GET request to the OpenRouter key endpoint to get current usage limits.

        Raises:
            LLMProviderError: If there is an error fetching the limits.
        """
        key_url = f"{self.api_url.rsplit('/', 1)[0]}/key"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            self.logger.debug(f"Fetching OpenRouter limits from: {key_url}")
            response = requests.get(key_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            limits_data = response.json()

            # Validate response structure
            # Check if the response has a 'data' key (new structure)
            if "data" in limits_data and isinstance(limits_data["data"], dict):
                data = limits_data["data"]
                # Check if the nested data has the required keys
                if "limit_remaining" in data and "rate_limit" in data:
                    self.openrouter_limits = data
                    self.logger.info(f"Updated OpenRouter limits: {data}")
                    return

            # Check for old structure (direct keys)
            elif "limit_remaining" in limits_data and "rate_limit" in limits_data:
                self.openrouter_limits = limits_data
                self.logger.info(f"Updated OpenRouter limits: {limits_data}")
                return

            # If we get here, the structure is invalid
            self.logger.warning(
                f"Invalid OpenRouter limits response structure: {limits_data}"
            )

        except Exception as e:
            self.logger.error(f"Error fetching OpenRouter limits: {e}")
            # Don't raise, just log the error

    def _check_openrouter_limits(self) -> None:
        """
        Check OpenRouter limits and wait or raise exception if needed.

        Raises:
            OpenRouterRateLimitError: If OpenRouter rate limits are exceeded.
        """
        if not self.openrouter_limits:
            return

        try:
            # Extract limit information
            limit_remaining = self.openrouter_limits.get("limit_remaining", 0)
            rate_limit = self.openrouter_limits.get("rate_limit", {})

            # Check if we're out of credits
            if limit_remaining <= 0:
                raise OpenRouterRateLimitError(
                    "OpenRouter credit limit exceeded",
                    limit_remaining,
                    rate_limit,
                )

            # Check if we need to wait for rate limit
            if (
                isinstance(rate_limit, dict)
                and "requests" in rate_limit
                and "interval" in rate_limit
            ):
                requests_allowed = rate_limit.get("requests", 0)
                interval_seconds = rate_limit.get("interval", 60)

                if requests_allowed <= 0:
                    # Calculate wait time based on interval
                    wait_time = interval_seconds
                    self.logger.warning(
                        f"OpenRouter rate limit reached. Waiting {wait_time} seconds."
                    )
                    time.sleep(wait_time)

        except OpenRouterRateLimitError:
            # Re-raise OpenRouterRateLimitError
            raise
        except Exception as e:
            # Log other errors but don't fail
            self.logger.error(f"Error checking OpenRouter limits: {e}")
