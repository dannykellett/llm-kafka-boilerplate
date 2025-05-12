# Environment Variables Documentation

This document provides a detailed description of all environment variables used by the LLM-Kafka Boilerplate, including their purpose, default values, validation rules, and examples.

## Kafka Configuration

### KAFKA_BOOTSTRAP_SERVERS

- **Description**: Comma-separated list of host:port pairs for Kafka brokers
- **Default**: None (required)
- **Validation**: Must be a non-empty string
- **Example**: `localhost:9092` or `broker1:9092,broker2:9092`

### KAFKA_INPUT_TOPIC

- **Description**: Name of the input Kafka topic to consume messages from
- **Default**: None (required)
- **Validation**: Must be a non-empty string
- **Example**: `input-topic`

### KAFKA_OUTPUT_TOPIC

- **Description**: Name of the output Kafka topic to produce results to
- **Default**: None (required)
- **Validation**: Must be a non-empty string
- **Example**: `output-topic`

### KAFKA_GROUP_ID

- **Description**: Consumer group ID for the Kafka consumer
- **Default**: None (required)
- **Validation**: Must be a non-empty string
- **Example**: `my-consumer-group`

### KAFKA_AUTO_OFFSET_RESET

- **Description**: What to do when there is no initial offset or the current offset is invalid
- **Default**: `earliest`
- **Validation**: Must be either `earliest` or `latest`
- **Example**: `earliest`

### KAFKA_ENABLE_AUTO_COMMIT

- **Description**: Whether to automatically commit offsets
- **Default**: `true`
- **Validation**: Must be a boolean (`true` or `false`)
- **Example**: `true`

## LLM Configuration

### LLM_API_KEY

- **Description**: API key for the LLM service
- **Default**: None (required)
- **Validation**: Must be a non-empty string
- **Example**: `sk-abcdefghijklmnopqrstuvwxyz123456`

### LLM_API_URL

- **Description**: URL for the LLM service API
- **Default**: None (required)
- **Validation**: Must be a valid HTTP URL
- **Example**: `https://api.openai.com/v1/chat/completions`

### LLM_MODEL

- **Description**: Model to use for the LLM service
- **Default**: None (required)
- **Validation**: Must be a non-empty string
- **Example**: `gpt-4` or `openai/gpt-4`

### LLM_TEMPERATURE

- **Description**: Temperature parameter for the LLM (controls randomness)
- **Default**: `0.2`
- **Validation**: Must be a float between 0.0 and 1.0
- **Example**: `0.2`

### LLM_MAX_TOKENS

- **Description**: Maximum number of tokens to generate in the LLM response
- **Default**: `500`
- **Validation**: Must be a positive integer
- **Example**: `500`

## Application Configuration

### LOG_LEVEL

- **Description**: Logging level
- **Default**: `INFO`
- **Validation**: Must be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `INFO`

### CACHE_TTL_SECONDS

- **Description**: Time-to-live for cache in seconds
- **Default**: `3600` (1 hour)
- **Validation**: Must be a positive integer
- **Example**: `3600`

## Custom Configuration

You can extend the configuration with your own environment variables by following these steps:

1. Create a custom settings class in your project:

```python
from pydantic import BaseModel, Field
from src.config.config import Settings

class CustomSettings(BaseModel):
    custom_setting_1: str = Field(..., min_length=1)
    custom_setting_2: int = Field(0, ge=0)

class ExtendedSettings(Settings):
    custom: CustomSettings
```

2. Update the `get_settings` function to load your custom settings:

```python
def get_extended_settings():
    # Load base settings
    base_settings = get_settings()
    
    # Load custom settings
    custom_settings = CustomSettings(
        custom_setting_1=os.getenv("CUSTOM_SETTING_1", "default"),
        custom_setting_2=int(os.getenv("CUSTOM_SETTING_2", "0")),
    )
    
    # Create and return extended settings
    return ExtendedSettings(
        kafka=base_settings.kafka,
        llm=base_settings.llm,
        app=base_settings.app,
        custom=custom_settings,
    )
```

3. Add your custom environment variables to your `.env` file:

```
CUSTOM_SETTING_1=value1
CUSTOM_SETTING_2=42
```

## Environment Variables Best Practices

1. **Security**: Never commit sensitive environment variables (like API keys) to version control
2. **Documentation**: Document all environment variables in your project's README
3. **Validation**: Always validate environment variables using Pydantic
4. **Defaults**: Provide sensible defaults for optional environment variables
5. **Naming**: Use a consistent naming convention for environment variables
6. **Grouping**: Group related environment variables with a common prefix