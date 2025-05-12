"""
Processor module for the LLM-Kafka Boilerplate.

This module provides the base class for processors.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.config.config import Settings
from src.llm.client import LLMClient

# Set up logging
logger = logging.getLogger(__name__)


class ProcessingError(Exception):
    """Exception raised for processing errors."""

    pass


class Processor(ABC):
    """
    Abstract base class for processors.

    This class defines the interface that all processors must implement.

    Attributes:
        settings: Application settings
        llm_client: LLM client for interacting with LLM services
    """

    def __init__(self, settings: Settings, llm_client: Optional[LLMClient] = None):
        """
        Initialize the processor.

        Args:
            settings: Application settings
            llm_client: LLM client for interacting with LLM services
        """
        self.settings = settings
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message.

        Args:
            message: The message to process

        Returns:
            Dict[str, Any]: The processed message

        Raises:
            ProcessingError: If there is an error processing the message
        """
        pass

    def validate_message(self, message: Dict[str, Any]) -> None:
        """
        Validate a message.

        This method can be overridden by subclasses to perform validation.

        Args:
            message: The message to validate

        Raises:
            ProcessingError: If the message is invalid
        """
        # Default implementation does nothing
        pass

    def preprocess(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess a message.

        This method can be overridden by subclasses to perform preprocessing.

        Args:
            message: The message to preprocess

        Returns:
            Dict[str, Any]: The preprocessed message

        Raises:
            ProcessingError: If there is an error preprocessing the message
        """
        # Default implementation returns the message unchanged
        return message

    def postprocess(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess a message.

        This method can be overridden by subclasses to perform postprocessing.

        Args:
            message: The message to postprocess

        Returns:
            Dict[str, Any]: The postprocessed message

        Raises:
            ProcessingError: If there is an error postprocessing the message
        """
        # Default implementation returns the message unchanged
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a message.

        This method orchestrates the processing of a message, including
        validation, preprocessing, processing, and postprocessing.

        Args:
            message: The message to handle

        Returns:
            Dict[str, Any]: The handled message

        Raises:
            ProcessingError: If there is an error handling the message
        """
        try:
            # Validate the message
            self.validate_message(message)

            # Preprocess the message
            preprocessed_message = self.preprocess(message)

            # Process the message
            processed_message = self.process(preprocessed_message)

            # Postprocess the message
            postprocessed_message = self.postprocess(processed_message)

            return postprocessed_message
        except ProcessingError:
            # Re-raise ProcessingError without wrapping it
            raise
        except Exception as e:
            # Wrap other exceptions in ProcessingError
            error_msg = f"Error handling message: {str(e)}"
            self.logger.error(error_msg)
            raise ProcessingError(error_msg) from e
