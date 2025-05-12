# Sentiment Analysis Example

This example demonstrates how to implement a sentiment analysis processor using the LLM-Kafka Boilerplate.

## Overview

In this example, we'll create a processor that:

1. Consumes messages containing text to analyze
2. Uses an LLM to perform sentiment analysis on the text
3. Produces results with sentiment classification (positive, negative, neutral) and confidence score

## Implementation Steps

### 1. Create a Custom Processor

Create a file `src/processing/sentiment_processor.py`:

```python
import logging
from typing import Any, Dict, Optional

from src.config.config import Settings
from src.llm.client import LLMClient
from src.processing.processor import Processor, ProcessingError

# Set up logging
logger = logging.getLogger(__name__)


class SentimentProcessor(Processor):
    """
    Processor for sentiment analysis.
    
    This processor analyzes the sentiment of text using an LLM.
    """

    def __init__(self, settings: Settings, llm_client: Optional[LLMClient] = None):
        """
        Initialize the sentiment processor.
        
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
        # Check for required fields
        if "id" not in message:
            raise ProcessingError("Missing required field: id")
            
        if "content" not in message:
            raise ProcessingError("Missing required field: content")
            
        # Check content is a string
        if not isinstance(message.get("content"), str):
            raise ProcessingError("Content must be a string")
            
        # Check content is not empty
        if not message.get("content").strip():
            raise ProcessingError("Content cannot be empty")

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
        if not self.llm_client:
            raise ProcessingError("LLM client is required for sentiment analysis")
            
        try:
            # Extract content
            content = message.get("content", "")
            
            # Create prompt for sentiment analysis
            prompt = f"""
            Analyze the sentiment of the following text and classify it as POSITIVE, NEGATIVE, or NEUTRAL.
            Also provide a confidence score between 0.0 and 1.0.
            
            Text: "{content}"
            
            Output your answer in JSON format:
            {{
                "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
                "confidence": 0.95,
                "explanation": "Brief explanation of the sentiment analysis"
            }}
            """
            
            # Generate response using LLM
            response = self.llm_client.generate(prompt)
            
            # Parse response
            import json
            try:
                sentiment_result = json.loads(response)
            except json.JSONDecodeError:
                # If response is not valid JSON, try to extract JSON using regex
                import re
                json_match = re.search(r'({.*})', response, re.DOTALL)
                if json_match:
                    sentiment_result = json.loads(json_match.group(1))
                else:
                    raise ProcessingError(f"Failed to parse LLM response: {response}")
            
            # Create result
            result = message.copy()
            result["result"] = {
                "sentiment": sentiment_result.get("sentiment", "NEUTRAL"),
                "confidence": sentiment_result.get("confidence", 0.5),
                "explanation": sentiment_result.get("explanation", "")
            }
            
            return result
            
        except Exception as e:
            raise ProcessingError(f"Error processing message: {str(e)}") from e
```

### 2. Register the Processor

Update your application initialization to register the sentiment processor:

```python
from src.processing.processor_factory import ProcessorFactory
from src.processing.sentiment_processor import SentimentProcessor

def register_processors(factory: ProcessorFactory) -> None:
    factory.register_processor("sentiment-analysis", SentimentProcessor)
    
# In your app.py or main module
def create_app():
    # ... existing code ...
    
    # Create processor factory
    processor_factory = ProcessorFactory(settings, llm_client)
    
    # Register processors
    register_processors(processor_factory)
    
    # ... rest of the code ...
```

### 3. Configure Environment Variables

Make sure your `.env` file includes the necessary configuration:

```
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_INPUT_TOPIC=sentiment-input
KAFKA_OUTPUT_TOPIC=sentiment-output
KAFKA_GROUP_ID=sentiment-analyzer
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_ENABLE_AUTO_COMMIT=true

# LLM Configuration
LLM_API_KEY=your-api-key
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=500

# Application Configuration
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=3600
```

### 4. Run the Application

```bash
python -m src
```

### 5. Send Test Messages

You can use a Kafka producer to send test messages:

```python
import json
import uuid
from confluent_kafka import Producer

# Configure the producer
producer = Producer({
    'bootstrap.servers': 'localhost:9092'
})

# Create a test message
message = {
    "id": str(uuid.uuid4()),
    "type": "sentiment-analysis",
    "content": "I absolutely love this product! It's amazing and has exceeded all my expectations.",
    "metadata": {
        "source": "example",
        "timestamp": "2025-05-12T14:30:00Z"
    }
}

# Produce the message
producer.produce(
    'sentiment-input',
    json.dumps(message).encode('utf-8'),
    callback=lambda err, msg: print(f"Delivered: {msg.value().decode('utf-8')}") if err is None else print(f"Error: {err}")
)

# Wait for any outstanding messages to be delivered
producer.flush()
```

### 6. Consume Results

You can use a Kafka consumer to consume the results:

```python
import json
from confluent_kafka import Consumer, KafkaError

# Configure the consumer
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'sentiment-result-consumer',
    'auto.offset.reset': 'earliest'
})

# Subscribe to the output topic
consumer.subscribe(['sentiment-output'])

# Consume messages
try:
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None:
            continue
            
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"Reached end of partition")
            else:
                print(f"Error: {msg.error()}")
        else:
            # Parse the message
            result = json.loads(msg.value().decode('utf-8'))
            
            # Print the result
            print(f"Sentiment: {result['result']['sentiment']}")
            print(f"Confidence: {result['result']['confidence']}")
            print(f"Explanation: {result['result']['explanation']}")
            print(f"Original text: {result['content']}")
            print("---")
            
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

## Expected Results

For the example message above, you might get a result like:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "sentiment-analysis",
  "content": "I absolutely love this product! It's amazing and has exceeded all my expectations.",
  "metadata": {
    "source": "example",
    "timestamp": "2025-05-12T14:30:00Z"
  },
  "result": {
    "sentiment": "POSITIVE",
    "confidence": 0.98,
    "explanation": "The text contains strong positive language ('absolutely love', 'amazing', 'exceeded all expectations') without any negative elements."
  }
}
```

## Extensions

You can extend this example in several ways:

1. **Add more sentiment categories**: Extend beyond positive/negative/neutral to include more nuanced emotions.

2. **Implement batch processing**: Process multiple messages at once for efficiency.

3. **Add caching**: Cache results for similar texts to reduce LLM API calls.

4. **Implement fallback mechanisms**: Use simpler rule-based sentiment analysis as a fallback if the LLM is unavailable.