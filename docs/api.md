# API Documentation

This document describes the APIs and interfaces provided by the LLM-Kafka Boilerplate, including message formats, extension points, and integration patterns.

## Kafka Message Formats

### Input Message Format

The boilerplate expects input messages in the following JSON format:

```json
{
  "id": "unique-message-id",
  "type": "message-type",
  "content": "Message content to process",
  "metadata": {
    "source": "source-system",
    "timestamp": "2025-05-12T14:30:00Z",
    "additional_field": "value"
  }
}
```

Key fields:
- `id`: Unique identifier for the message
- `type`: Type of message, used to route to the appropriate processor
- `content`: The main content to be processed
- `metadata`: Additional information about the message

### Output Message Format

The boilerplate produces output messages in the following JSON format:

```json
{
  "id": "unique-message-id",
  "original": {
    "content": "Original message content",
    "type": "message-type"
  },
  "result": {
    "processed_content": "Processed content",
    "confidence": 0.95,
    "additional_field": "value"
  },
  "metadata": {
    "source": "source-system",
    "timestamp": "2025-05-12T14:30:00Z",
    "processing_time_ms": 1234,
    "processor": "CustomProcessor"
  }
}
```

Key fields:
- `id`: Same identifier as the input message
- `original`: Original message content and type
- `result`: Processing result with relevant fields
- `metadata`: Additional information about the processing

## Extension Points

### Custom Processors

The boilerplate provides an extension point for custom processors through the `Processor` abstract base class:

```python
from src.processing.processor import Processor

class CustomProcessor(Processor):
    def validate_message(self, message):
        # Custom validation logic
        pass
        
    def preprocess(self, message):
        # Custom preprocessing logic
        return preprocessed_message
        
    def process(self, message):
        # Custom processing logic
        return processed_message
        
    def postprocess(self, message):
        # Custom postprocessing logic
        return postprocessed_message
```

To register a custom processor:

```python
from src.processing.processor_factory import ProcessorFactory
from your_module import CustomProcessor

def register_processors(factory: ProcessorFactory) -> None:
    factory.register_processor("custom-type", CustomProcessor)
```

### Custom LLM Providers

The boilerplate provides an extension point for custom LLM providers through the `LLMProvider` abstract base class:

```python
from src.llm.providers.base import LLMProvider

class CustomProvider(LLMProvider):
    def __init__(self, api_key, api_url, model, temperature=0.2, max_tokens=500, timeout=30):
        # Initialize provider
        pass
        
    def generate(self, prompt):
        # Custom generation logic
        return response
        
    def get_metrics(self):
        # Return metrics
        return metrics
```

To register a custom LLM provider:

```python
from src.llm.client import LLMProviderFactory
from your_module import CustomProvider

# Monkey patch the factory's create_provider method
original_create_provider = LLMProviderFactory.create_provider

def custom_create_provider(settings):
    # Check if we should use the custom provider
    if "custom" in settings.llm.api_url:
        return CustomProvider(
            api_key=settings.llm.api_key,
            api_url=settings.llm.api_url,
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            max_tokens=settings.llm.max_tokens,
        )
    # Otherwise, use the original factory method
    return original_create_provider(settings)

# Replace the factory method
LLMProviderFactory.create_provider = staticmethod(custom_create_provider)
```

### Custom Configuration

The boilerplate provides an extension point for custom configuration through Pydantic models:

```python
from pydantic import BaseModel, Field
from src.config.config import Settings

class CustomSettings(BaseModel):
    custom_setting_1: str = Field(..., min_length=1)
    custom_setting_2: int = Field(0, ge=0)

class ExtendedSettings(Settings):
    custom: CustomSettings
```

To use the extended settings:

```python
from templates.config.custom_config import get_extended_settings

# Replace the original get_settings function
from src.config import config
config.get_settings = get_extended_settings
```

## Integration Patterns

### Producer-Consumer Pattern

The boilerplate implements the producer-consumer pattern for asynchronous message processing:

1. Producers send messages to Kafka input topics
2. The boilerplate consumes messages from input topics
3. Messages are processed by the appropriate processor
4. Results are produced to Kafka output topics
5. Consumers read results from output topics

### Request-Response Pattern

For synchronous processing, you can implement a request-response pattern:

1. Add a `correlation_id` field to input messages
2. Configure the processor to include the `correlation_id` in output messages
3. Implement a response handler that matches responses to requests by `correlation_id`

Example:

```python
# Producer side
correlation_id = str(uuid.uuid4())
message = {
    "id": "msg-123",
    "type": "text-analysis",
    "content": "This is a sample text to analyze.",
    "correlation_id": correlation_id,
    "metadata": {
        "source": "web",
        "timestamp": "2025-05-12T14:30:00Z"
    }
}
kafka_producer.produce(input_topic, json.dumps(message).encode('utf-8'))

# Consumer side
def handle_response(response):
    correlation_id = response.get("correlation_id")
    if correlation_id in pending_requests:
        request = pending_requests.pop(correlation_id)
        # Process response for the request
```

### Batch Processing Pattern

For batch processing, you can implement a batch processor:

```python
class BatchProcessor(Processor):
    def __init__(self, settings, llm_client, batch_size=10):
        super().__init__(settings, llm_client)
        self.batch_size = batch_size
        self.batch = []
        
    def process(self, message):
        # Add message to batch
        self.batch.append(message)
        
        # If batch is full, process it
        if len(self.batch) >= self.batch_size:
            return self._process_batch()
            
        # Otherwise, return None to indicate no result yet
        return None
        
    def _process_batch(self):
        # Process the batch
        results = []
        for msg in self.batch:
            # Process each message
            results.append(processed_msg)
            
        # Clear the batch
        self.batch = []
        
        return results
```

## API Versioning

The boilerplate supports API versioning through message schemas:

1. Include a `version` field in your messages:

```json
{
  "id": "unique-message-id",
  "type": "message-type",
  "version": "1.0",
  "content": "Message content to process"
}
```

2. Implement version-specific processors:

```python
class ProcessorV1(Processor):
    def process(self, message):
        # V1 processing logic
        return processed_message

class ProcessorV2(Processor):
    def process(self, message):
        # V2 processing logic
        return processed_message
```

3. Register version-specific processors:

```python
def register_processors(factory: ProcessorFactory) -> None:
    factory.register_processor("custom-type-v1", ProcessorV1)
    factory.register_processor("custom-type-v2", ProcessorV2)
```

4. Route messages based on type and version:

```python
def get_processor_type(message):
    base_type = message.get("type", "default")
    version = message.get("version", "1.0")
    return f"{base_type}-v{version.split('.')[0]}"