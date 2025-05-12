"""
Configuration module for the LLM-Kafka Boilerplate.

This module provides configuration settings for the application using Pydantic for validation.
It loads configuration from environment variables and provides a centralized location for
all configuration settings.
"""

import os
import logging
from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator
from dotenv import load_dotenv


# Set up logging
logger = logging.getLogger(__name__)


# Load environment variables from .env file
def load_env_vars():
    """
    Load environment variables from .env file if it exists.
    """
    env_path = os.path.join(os.getcwd(), ".env")
    logger.info(f"Looking for environment variables in: {env_path}")

    # Check if file exists
    if os.path.exists(env_path):
        logger.info(f".env file exists at {env_path}")
        # Load environment variables from the .env file
        try:
            load_dotenv(dotenv_path=env_path, override=True)
            logger.info("Successfully loaded environment variables from .env file")
        except Exception as e:
            logger.warning(f"Error loading environment variables from .env file: {e}")
            logger.warning("Will rely on environment variables passed to the container")
    else:
        logger.warning(f".env file does not exist at {env_path}")
        logger.warning("Will rely on environment variables passed to the container")


class KafkaSettings(BaseModel):
    """
    Kafka configuration settings.

    Attributes:
        bootstrap_servers: Comma-separated list of host:port pairs for Kafka brokers
        input_topic: Name of the input Kafka topic
        output_topic: Name of the output Kafka topic
        group_id: Consumer group ID for the Kafka consumer
        auto_offset_reset: What to do when there is no initial offset or the current offset is invalid
        enable_auto_commit: Whether to automatically commit offsets
    """

    bootstrap_servers: str = Field(..., min_length=1)
    input_topic: str = Field(..., min_length=1)
    output_topic: str = Field(..., min_length=1)
    group_id: str = Field(..., min_length=1)
    auto_offset_reset: Literal["earliest", "latest"] = "earliest"
    enable_auto_commit: bool = True

    @field_validator("bootstrap_servers")
    @classmethod
    def validate_bootstrap_servers(cls, v: str) -> str:
        """Validate bootstrap_servers is not empty."""
        if not v:
            raise ValueError("bootstrap_servers cannot be empty")
        return v

    @field_validator("input_topic", "output_topic", "group_id")
    @classmethod
    def validate_topic_names(cls, v: str) -> str:
        """Validate topic names are not empty."""
        if not v:
            raise ValueError("Topic names cannot be empty")
        return v


class LLMSettings(BaseModel):
    """
    LLM configuration settings.

    Attributes:
        api_key: API key for the LLM service
        api_url: URL for the LLM service API
        model: Model to use for the LLM service
        temperature: Temperature parameter for the LLM (controls randomness)
        max_tokens: Maximum number of tokens to generate in the LLM response
    """

    api_key: str = Field(..., min_length=1)
    api_url: HttpUrl
    model: str = Field(..., min_length=1)
    temperature: float = Field(0.2, ge=0.0, le=1.0)
    max_tokens: int = Field(500, gt=0)

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate api_key is not empty."""
        if not v:
            raise ValueError("api_key cannot be empty")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model is not empty."""
        if not v:
            raise ValueError("model cannot be empty")
        return v


class ApplicationSettings(BaseModel):
    """
    Application configuration settings.

    Attributes:
        log_level: Logging level
        cache_ttl_seconds: Time-to-live for cache in seconds
    """

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    cache_ttl_seconds: int = Field(3600, gt=0)


class Settings(BaseModel):
    """
    Application settings.

    Attributes:
        kafka: Kafka configuration settings
        llm: LLM configuration settings
        app: Application configuration settings
    """

    kafka: KafkaSettings
    llm: LLMSettings
    app: ApplicationSettings


def get_settings() -> Settings:
    """
    Load settings from environment variables.

    Returns:
        Settings: Application settings

    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    # Load environment variables from .env file
    load_env_vars()

    # Load Kafka settings from environment variables
    kafka_settings = KafkaSettings(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", ""),
        input_topic=os.getenv("KAFKA_INPUT_TOPIC", ""),
        output_topic=os.getenv("KAFKA_OUTPUT_TOPIC", ""),
        group_id=os.getenv("KAFKA_GROUP_ID", ""),
        auto_offset_reset=os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest"),
        enable_auto_commit=os.getenv("KAFKA_ENABLE_AUTO_COMMIT", "true").lower()
        == "true",
    )

    # Load LLM settings from environment variables
    llm_settings = LLMSettings(
        api_key=os.getenv("LLM_API_KEY", ""),
        api_url=os.getenv("LLM_API_URL", ""),
        model=os.getenv("LLM_MODEL", ""),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "500")),
    )

    # Load application settings from environment variables
    app_settings = ApplicationSettings(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
    )

    # Log Kafka settings for debugging
    logger.info(
        f"Loaded Kafka settings: group_id={kafka_settings.group_id}, "
        f"bootstrap_servers={kafka_settings.bootstrap_servers}, "
        f"auto_offset_reset={kafka_settings.auto_offset_reset}"
    )

    # Create and return settings
    return Settings(
        kafka=kafka_settings,
        llm=llm_settings,
        app=app_settings,
    )
