# Data Flow Documentation

This document describes the flow of data through the LLM-Kafka Boilerplate, including message transformations, error handling, and recovery mechanisms.

## Message Flow Overview

The LLM-Kafka Boilerplate processes messages in a pipeline, with each stage transforming the message in some way:

1. **Kafka Consumer**: Consumes messages from Kafka input topics
2. **Message Validation**: Validates message structure and content
3. **Message Preprocessing**: Normalizes and prepares the message
4. **Message Processing**: Applies business logic and LLM integration
5. **Message Postprocessing**: Adds metadata and formats the result
6. **Kafka Producer**: Produces results to Kafka output topics

## Detailed Message Flow

### 1. Message Consumption

Messages are consumed from Kafka using the `KafkaConsumerWorker`. The consumed message is a JSON object deserialized into a Python dictionary.

### 2. Message Validation

Messages are validated by the processor's `validate_message` method to ensure they have the required fields with correct types and values.

### 3. Message Preprocessing

Messages are preprocessed by the processor's `preprocess` method, which can include normalizing field values, adding defaults, and filtering.

### 4. Message Processing

Messages are processed by the processor's `process` method, which implements the core business logic including LLM integration if needed.

### 5. LLM Integration

If needed, the processor can use the LLM client to generate text. The LLM client handles provider selection, rate limiting, retries, and error handling.

### 6. Message Postprocessing

Messages are postprocessed by the processor's `postprocess` method, which can add metadata, format the response, and add timestamps.

### 7. Result Production

Results are produced to Kafka using the `KafkaProducerWorker`. The result is a JSON object serialized from a Python dictionary.

## Error Handling and Recovery

The boilerplate implements several error handling and recovery mechanisms:

### 1. Exception Handling

Each stage of the pipeline has specific exception handling:

```python
try:
    # Process message
except ProcessingError as e:
    logger.error(f"Processing error: {e}")
except KafkaError as e:
    logger.error(f"Kafka error: {e}")
except LLMProviderError as e:
    logger.error(f"LLM provider error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### 2. Retry Mechanism

The boilerplate includes a retry decorator for handling transient errors:

```python
@retry(max_retries=3, retry_delay=1.0, backoff_factor=2.0)
def some_function():
    # Function that might fail transiently
```

### 3. Dead Letter Queue

For messages that cannot be processed after retries, they can be sent to a dead letter queue:

```python
def handle_failed_message(message, error):
    # Send to dead letter queue
    self.kafka_service.produce_message(
        {
            "original_message": message,
            "error": str(error),
            "timestamp": time.time()
        },
        topic="dead-letter-queue"
    )
```

### 4. Circuit Breaker

For external services that are failing, a circuit breaker can be implemented:

```python
if self.circuit_breaker.is_open():
    # Use fallback mechanism
    return fallback_result
```

## Monitoring and Observability

The boilerplate includes several monitoring and observability features:

### 1. Metrics Collection

The `MetricsCollector` class collects metrics about message processing:

```python
self.metrics.start_timer("message_processing")
# Process message
processing_time = self.metrics.stop_timer("message_processing")
```

### 2. Logging

Comprehensive logging is implemented throughout the codebase:

```python
logger.info(f"Processing message of type: {message_type}")
logger.debug(f"Message content: {message}")
logger.error(f"Error processing message: {e}")
```

### 3. Tracing

Message IDs are propagated through the pipeline for tracing:

```python
logger.info(f"Processing message with ID {message.get('id', 'unknown')}")