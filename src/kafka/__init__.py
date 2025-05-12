"""
Kafka module for the LLM-Kafka Boilerplate.

This module provides functionality for interacting with Kafka, including consuming
messages from input topics and producing messages to output topics.
"""

from src.kafka.kafka_service import KafkaService, KafkaError, MessageSerializationError

__all__ = ["KafkaService", "KafkaError", "MessageSerializationError"]
