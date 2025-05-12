"""
OpenAI LLM provider module for the LLM-Kafka Boilerplate.

This module provides an implementation of the LLMProvider interface for OpenAI.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

import requests

from src.llm.providers.base import LLMProvider, LLMProviderError, RateLimitError

# Set up logging
logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider implementation.

    This class implements the LLMProvider interface for OpenAI.

    Attributes:
        api_key: API key for the OpenAI service.
        api_url: URL for the OpenAI service API.
        model: Model to use for generation.
        temperature: Temperature parameter for generation.
        max_tokens: Maximum number of tokens to generate.
        timeout: Timeout for API requests in seconds.
        metrics: Metrics from the last generation.
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
        Initialize the OpenAI provider.

        Args:
            api_key: API key for the OpenAI service.
            api_url: URL for the OpenAI service API.
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
        self.logger = logging.getLogger(__name__)

    def generate(self, prompt: str) -> str:
        """
        Generate a response using the OpenAI API.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            str: The generated response.

        Raises:
            LLMProviderError: If there is an error generating the response.
            RateLimitError: If rate limits are exceeded.
        """
        try:
            self.logger.debug(f"Sending request to OpenAI API: {self.api_url}")

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
                raise LLMProviderError("No choices in OpenAI response")

            # Store metrics
            self.metrics = {
                "token_usage": response_data.get("usage", {}),
                "model_info": self.model,
                "response_time": response_time,
                "status_code": response.status_code,
            }

            return generated_text

        except requests.exceptions.HTTPError as e:
            # Check for rate limit error
            if e.response.status_code == 429:
                self.logger.warning(f"OpenAI rate limit exceeded: {e}")
                raise RateLimitError(f"OpenAI rate limit exceeded: {e}")

            self.logger.error(f"HTTP error from OpenAI API: {e}")
            raise LLMProviderError(f"HTTP error from OpenAI API: {e}")

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error to OpenAI API: {e}")
            raise LLMProviderError(f"Connection error to OpenAI API: {e}")

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout connecting to OpenAI API: {e}")
            raise LLMProviderError(f"Timeout connecting to OpenAI API: {e}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from OpenAI API: {e}")
            raise LLMProviderError(f"Invalid JSON response from OpenAI API: {e}")

        except Exception as e:
            self.logger.error(f"Unexpected error with OpenAI API: {e}")
            raise LLMProviderError(f"Unexpected error with OpenAI API: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from the last generation.

        Returns:
            Dict[str, Any]: Metrics from the last generation.
        """
        return self.metrics
