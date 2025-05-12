"""
Custom configuration template for the LLM-Kafka Boilerplate.

This template provides a starting point for implementing custom configuration.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field

from src.config.config import Settings


class CustomSettings(BaseModel):
    """
    Custom configuration settings.

    This class defines custom configuration settings for your application.

    Attributes:
        custom_setting_1: First custom setting
        custom_setting_2: Second custom setting
        custom_setting_3: Third custom setting
    """

    custom_setting_1: str = Field(..., min_length=1)
    custom_setting_2: int = Field(0, ge=0)
    custom_setting_3: Optional[str] = None


class ExtendedSettings(Settings):
    """
    Extended application settings.

    This class extends the base Settings class with custom settings.

    Attributes:
        custom: Custom configuration settings
    """

    custom: CustomSettings


def get_extended_settings() -> ExtendedSettings:
    """
    Load extended settings from environment variables.

    Returns:
        ExtendedSettings: Extended application settings

    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    # Load base settings
    base_settings = Settings(
        kafka=Settings.model_fields["kafka"].annotation(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", ""),
            input_topic=os.getenv("KAFKA_INPUT_TOPIC", ""),
            output_topic=os.getenv("KAFKA_OUTPUT_TOPIC", ""),
            group_id=os.getenv("KAFKA_GROUP_ID", ""),
            auto_offset_reset=os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest"),
            enable_auto_commit=os.getenv("KAFKA_ENABLE_AUTO_COMMIT", "true").lower()
            == "true",
        ),
        llm=Settings.model_fields["llm"].annotation(
            api_key=os.getenv("LLM_API_KEY", ""),
            api_url=os.getenv("LLM_API_URL", ""),
            model=os.getenv("LLM_MODEL", ""),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "500")),
        ),
        app=Settings.model_fields["app"].annotation(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
        ),
    )

    # Load custom settings
    custom_settings = CustomSettings(
        custom_setting_1=os.getenv("CUSTOM_SETTING_1", "default"),
        custom_setting_2=int(os.getenv("CUSTOM_SETTING_2", "0")),
        custom_setting_3=os.getenv("CUSTOM_SETTING_3"),
    )

    # Create and return extended settings
    return ExtendedSettings(
        kafka=base_settings.kafka,
        llm=base_settings.llm,
        app=base_settings.app,
        custom=custom_settings,
    )


# To use the extended settings in your application, replace the get_settings function:
#
# from templates.config.custom_config import get_extended_settings
#
# # Replace the original get_settings function
# from src.config import config
# config.get_settings = get_extended_settings