"""
Rate limiter module for the LLM-Kafka Boilerplate.

This module provides rate limiting functionality for LLM API calls.
"""

import logging
import threading
import time
from typing import Dict, Optional

# Set up logging
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter for API calls.

    This class implements a token bucket algorithm for rate limiting API calls.

    Attributes:
        rpm_limit: Requests per minute limit
        tokens: Current number of tokens in the bucket
        last_refill: Time of the last token refill
        lock: Lock for thread-safe access to the token bucket
    """

    def __init__(self, rpm_limit: int = 3):
        """
        Initialize the rate limiter.

        Args:
            rpm_limit: Requests per minute limit (default: 3)
        """
        self.rpm_limit = rpm_limit
        self.tokens = rpm_limit
        self.last_refill = time.time()
        self.lock = threading.RLock()

    def acquire(self) -> float:
        """
        Acquire a token from the bucket.

        This method attempts to acquire a token from the bucket, waiting if necessary.
        It returns the time to wait before making the API call.

        Returns:
            float: Time to wait before making the API call (in seconds)
        """
        with self.lock:
            # Refill tokens based on time elapsed
            now = time.time()
            time_elapsed = now - self.last_refill
            tokens_to_add = time_elapsed * (self.rpm_limit / 60.0)
            self.tokens = min(self.rpm_limit, self.tokens + tokens_to_add)
            self.last_refill = now

            # If we have tokens, consume one and return 0 wait time
            if self.tokens >= 1:
                self.tokens -= 1
                return 0.0

            # Calculate wait time
            wait_time = (1 - self.tokens) * (60.0 / self.rpm_limit)
            logger.info(f"Rate limit reached. Need to wait {wait_time:.2f} seconds.")
            return wait_time


# Global rate limiter instance with lock
_global_rate_limiter: Dict[str, RateLimiter] = {}
_lock = threading.RLock()


def global_rate_limit(min_delay_seconds: int = 60) -> float:
    """
    Apply global rate limiting across all LLM providers.

    This function ensures a minimum delay between API calls across all providers.

    Args:
        min_delay_seconds: Minimum delay between API calls in seconds (default: 60)

    Returns:
        float: Time to wait before making the API call (in seconds)
    """
    with _lock:
        # Get or create the global rate limiter
        if "global" not in _global_rate_limiter:
            rpm = 60.0 / min_delay_seconds
            _global_rate_limiter["global"] = RateLimiter(rpm_limit=rpm)

        # Acquire a token
        wait_time = _global_rate_limiter["global"].acquire()

        # If we need to wait, sleep for that amount of time
        if wait_time > 0:
            logger.info(f"Global rate limit: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)

        return wait_time


def get_provider_rate_limiter(provider_name: str, rpm_limit: int = 3) -> RateLimiter:
    """
    Get a rate limiter for a specific provider.

    Args:
        provider_name: Name of the provider
        rpm_limit: Requests per minute limit (default: 3)

    Returns:
        RateLimiter: Rate limiter for the provider
    """
    with _lock:
        if provider_name not in _global_rate_limiter:
            _global_rate_limiter[provider_name] = RateLimiter(rpm_limit=rpm_limit)
        return _global_rate_limiter[provider_name]
