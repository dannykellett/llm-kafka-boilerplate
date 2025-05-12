"""
Processing module for the LLM-Kafka Boilerplate.

This module provides functionality for processing messages, including
base processor class and processor factory.
"""

from src.processing.processor import Processor, ProcessingError
from src.processing.processor_factory import ProcessorFactory

__all__ = ["Processor", "ProcessingError", "ProcessorFactory"]
