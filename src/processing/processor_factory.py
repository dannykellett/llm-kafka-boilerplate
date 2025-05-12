"""
Processor factory module for the LLM-Kafka Boilerplate.

This module provides a factory for creating processors.
"""

import logging
from typing import Dict, Type

from src.config.config import Settings
from src.llm.client import LLMClient
from src.processing.processor import Processor, ProcessingError

# Set up logging
logger = logging.getLogger(__name__)


class ProcessorFactory:
    """
    Factory for creating processors.

    This class provides methods for registering and creating processors.

    Attributes:
        settings: Application settings
        llm_client: LLM client for interacting with LLM services
        processors: Dictionary mapping processor names to processor classes
    """

    def __init__(self, settings: Settings, llm_client: LLMClient):
        """
        Initialize the processor factory.

        Args:
            settings: Application settings
            llm_client: LLM client for interacting with LLM services
        """
        self.settings = settings
        self.llm_client = llm_client
        self.processors: Dict[str, Type[Processor]] = {}
        self.logger = logging.getLogger(__name__)

    def register_processor(self, name: str, processor_class: Type[Processor]) -> None:
        """
        Register a processor.

        Args:
            name: Name of the processor
            processor_class: Processor class
        """
        self.logger.info(f"Registering processor: {name}")
        self.processors[name] = processor_class

    def create_processor(self, name: str) -> Processor:
        """
        Create a processor.

        Args:
            name: Name of the processor

        Returns:
            Processor: The created processor

        Raises:
            ProcessingError: If the processor is not registered
        """
        if name not in self.processors:
            error_msg = f"Processor not registered: {name}"
            self.logger.error(error_msg)
            raise ProcessingError(error_msg)

        self.logger.info(f"Creating processor: {name}")
        processor_class = self.processors[name]
        return processor_class(self.settings, self.llm_client)

    def get_registered_processors(self) -> Dict[str, Type[Processor]]:
        """
        Get registered processors.

        Returns:
            Dict[str, Type[Processor]]: Dictionary mapping processor names to processor classes
        """
        return self.processors.copy()
