"""
Custom processor template for the LLM-Kafka Boilerplate.

This template provides a starting point for implementing a custom processor.
"""

import logging
from typing import Any, Dict, Optional

from src.config.config import Settings
from src.llm.client import LLMClient
from src.processing.processor import Processor, ProcessingError

# Set up logging
logger = logging.getLogger(__name__)


class CustomProcessor(Processor):
    """
    Custom processor implementation.

    This class implements a custom processor for handling specific message types.

    Attributes:
        settings: Application settings
        llm_client: LLM client for interacting with LLM services
    """

    def __init__(self, settings: Settings, llm_client: Optional[LLMClient] = None):
        """
        Initialize the custom processor.

        Args:
            settings: Application settings
            llm_client: LLM client for interacting with LLM services
        """
        super().__init__(settings, llm_client)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def validate_message(self, message: Dict[str, Any]) -> None:
        """
        Validate a message.

        Args:
            message: The message to validate

        Raises:
            ProcessingError: If the message is invalid
        """
        # Implement message validation logic here
        # For example, check for required fields
        required_fields = ["id", "content"]
        for field in required_fields:
            if field not in message:
                raise ProcessingError(f"Missing required field: {field}")

    def preprocess(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess a message.

        Args:
            message: The message to preprocess

        Returns:
            Dict[str, Any]: The preprocessed message

        Raises:
            ProcessingError: If there is an error preprocessing the message
        """
        # Implement message preprocessing logic here
        # For example, transform or normalize fields
        preprocessed_message = message.copy()
        
        # Example: Convert content to lowercase
        if "content" in preprocessed_message:
            preprocessed_message["content"] = preprocessed_message["content"].lower()
            
        return preprocessed_message

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
        # Implement message processing logic here
        # For example, use the LLM client to generate a response
        processed_message = message.copy()
        
        try:
            # Example: Use LLM to generate a response
            if self.llm_client and "content" in processed_message:
                prompt = f"Process the following content: {processed_message['content']}"
                response = self.llm_client.generate(prompt)
                processed_message["response"] = response
                
            # Add processing metadata
            processed_message["processed"] = True
            processed_message["processor"] = self.__class__.__name__
            
            return processed_message
            
        except Exception as e:
            raise ProcessingError(f"Error processing message: {str(e)}") from e

    def postprocess(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess a message.

        Args:
            message: The message to postprocess

        Returns:
            Dict[str, Any]: The postprocessed message

        Raises:
            ProcessingError: If there is an error postprocessing the message
        """
        # Implement message postprocessing logic here
        # For example, add additional metadata or format the response
        postprocessed_message = message.copy()
        
        # Example: Add timestamp
        import datetime
        postprocessed_message["timestamp"] = datetime.datetime.now().isoformat()
        
        return postprocessed_message


# To register this processor with the factory, add the following code to your application:
#
# from src.processing.processor_factory import ProcessorFactory
# from templates.processor.custom_processor import CustomProcessor
#
# def register_processors(factory: ProcessorFactory) -> None:
#     factory.register_processor("custom", CustomProcessor)