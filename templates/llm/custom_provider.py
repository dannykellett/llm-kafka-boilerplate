"""
Custom LLM provider template for the LLM-Kafka Boilerplate.

This template provides a starting point for implementing a custom LLM provider.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

import requests

from src.llm.providers.base import LLMProvider, LLMProviderError, RateLimitError

# Set up logging
logger = logging.getLogger(__name__)


class CustomProviderError(LLMProviderError):
    """Exception raised for custom provider errors."""

    pass


class CustomProvider(LLMProvider):
    """
    Custom LLM provider implementation.

    This class implements the LLMProvider interface for a custom LLM service.

    Attributes:
        api_key: API key for the LLM service.
        api_url: URL for the LLM service API.
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
        Initialize the custom provider.

        Args:
            api_key: API key for the LLM service.
            api_url: URL for the LLM service API.
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
        Generate a response using the custom LLM API.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            str: The generated response.

        Raises:
            LLMProviderError: If there is an error generating the response.
            RateLimitError: If rate limits are exceeded.
        """
        try:
            self.logger.debug(f"Sending request to custom LLM API: {self.api_url}")

            # Prepare the request payload
            # Modify this to match your API's expected format
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            # Prepare headers
            # Modify this to match your API's expected authentication method
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
            # Modify this to match your API's response format
            if "text" in response_data:
                generated_text = response_data["text"]
            else:
                raise CustomProviderError("No text in custom LLM response")

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
                self.logger.warning(f"Custom LLM rate limit exceeded: {e}")
                raise RateLimitError(f"Custom LLM rate limit exceeded: {e}")

            self.logger.error(f"HTTP error from custom LLM API: {e}")
            raise CustomProviderError(f"HTTP error from custom LLM API: {e}")

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error to custom LLM API: {e}")
            raise CustomProviderError(f"Connection error to custom LLM API: {e}")

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout connecting to custom LLM API: {e}")
            raise CustomProviderError(f"Timeout connecting to custom LLM API: {e}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from custom LLM API: {e}")
            raise CustomProviderError(f"Invalid JSON response from custom LLM API: {e}")

        except Exception as e:
            self.logger.error(f"Unexpected error with custom LLM API: {e}")
            raise CustomProviderError(f"Unexpected error with custom LLM API: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from the last generation.

        Returns:
            Dict[str, Any]: Metrics from the last generation.
        """
        return self.metrics


# To register this provider with the factory, add the following code to your application:
#
# from src.llm.client import LLMProviderFactory
# from templates.llm.custom_provider import CustomProvider
#
# # Monkey patch the factory's create_provider method
# original_create_provider = LLMProviderFactory.create_provider
#
# def custom_create_provider(settings):
#     # Check if we should use the custom provider
#     if "custom" in settings.llm.api_url:
#         return CustomProvider(
#             api_key=settings.llm.api_key,
#             api_url=settings.llm.api_url,
#             model=settings.llm.model,
#             temperature=settings.llm.temperature,
#             max_tokens=settings.llm.max_tokens,
#         )
#     # Otherwise, use the original factory method
#     return original_create_provider(settings)
#
# # Replace the factory method
# LLMProviderFactory.create_provider = staticmethod(custom_create_provider)