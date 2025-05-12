"""
Error handling utilities for the LLM-Kafka Boilerplate.

This module provides utilities for handling errors and implementing retries.
"""

import functools
import logging
import time
from typing import Any, Callable, List, Optional, Type, TypeVar, cast

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for function return type
T = TypeVar("T")


def handle_exception(
    exception: Exception,
    error_message: str,
    logger: Optional[logging.Logger] = None,
    raise_exception: bool = True,
    exception_type: Type[Exception] = Exception,
) -> None:
    """
    Handle an exception.

    Args:
        exception: The exception to handle
        error_message: Error message to log
        logger: Logger to use (if None, uses module logger)
        raise_exception: Whether to raise the exception after handling
        exception_type: Type of exception to raise (if raise_exception is True)

    Raises:
        Exception: The handled exception (if raise_exception is True)
    """
    # Use module logger if not provided
    log = logger or logging.getLogger(__name__)

    # Log the error
    log.error(f"{error_message}: {str(exception)}")

    # Raise the exception if requested
    if raise_exception:
        raise exception_type(f"{error_message}: {str(exception)}") from exception


def retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: List[Type[Exception]] = None,
    logger: Optional[logging.Logger] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying a function on exception.

    Args:
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries in seconds
        backoff_factor: Factor to increase delay for each retry
        exceptions: List of exceptions to retry on (if None, retries on all exceptions)
        logger: Logger to use (if None, uses module logger)

    Returns:
        Callable: Decorated function
    """
    # Use module logger if not provided
    log = logger or logging.getLogger(__name__)

    # Default to all exceptions if not specified
    if exceptions is None:
        exceptions = [Exception]

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            delay = retry_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions) as e:
                    last_exception = e
                    if attempt < max_retries:
                        log.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        log.error(
                            f"All {max_retries + 1} attempts failed. Last error: {str(e)}"
                        )

            # If we get here, all retries failed
            if last_exception:
                raise last_exception

            # This should never happen, but just in case
            raise RuntimeError("Unexpected error in retry decorator")

        return cast(Callable[..., T], wrapper)

    return decorator
