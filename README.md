# LLM-Kafka Boilerplate

A flexible boilerplate for building applications that integrate Kafka messaging with LLM services.

## Features

- **Kafka Integration**: Consume messages from Kafka topics and produce results back to Kafka
- **LLM Integration**: Interact with LLM services through a unified interface
- **Extensible Architecture**: Easily extend with custom processors and LLM providers
- **Configuration Management**: Centralized configuration using Pydantic for validation
- **Error Handling**: Robust error handling and retry mechanisms
- **Metrics Collection**: Built-in metrics collection for monitoring
- **Docker Support**: Ready-to-use Docker and Docker Compose configurations

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Access to a Kafka cluster
- API key for an LLM service (OpenAI, OpenRouter, etc.)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/llm-kafka-boilerplate.git
cd llm-kafka-boilerplate
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
make install  # For production dependencies
# or
make install-dev  # For development dependencies
```

### Configuration

1. Create a `.env` file based on the example:

```
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_INPUT_TOPIC=input-topic
KAFKA_OUTPUT_TOPIC=output-topic
KAFKA_GROUP_ID=my-consumer-group
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

### Running the Application

```bash
# Run directly
make run

# Or using Docker
make docker-build
make docker-run
```

## Extending the Boilerplate

### Custom Processors

1. Create a new processor by extending the base `Processor` class:

```python
from src.processing.processor import Processor

class CustomProcessor(Processor):
    def process(self, message):
        # Custom processing logic
        return processed_result
```

2. Register the processor in the factory:

```python
from src.processing.processor_factory import ProcessorFactory
from your_module import CustomProcessor

def register_processors(factory: ProcessorFactory) -> None:
    factory.register_processor("custom", CustomProcessor)
```

### Custom LLM Providers

1. Create a new provider by extending the base `LLMProvider` class:

```python
from src.llm.providers.base import LLMProvider

class CustomProvider(LLMProvider):
    def generate(self, prompt):
        # Custom generation logic
        return response
```

2. Register the provider in the factory:

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

## Project Structure

```
llm-kafka-boilerplate/
├── src/                          # Source code
│   ├── config/                   # Configuration module
│   ├── kafka/                    # Kafka module
│   ├── llm/                      # LLM module
│   │   └── providers/            # LLM providers
│   ├── data/                     # Data management module
│   ├── processing/               # Processing module
│   └── utils/                    # Utility module
├── templates/                    # Templates for project-specific implementations
├── tests/                        # Tests
├── docs/                         # Documentation
├── .env.example                  # Example environment variables
├── Dockerfile                    # Dockerfile for containerization
├── docker-compose.yml            # Docker Compose configuration
├── Makefile                      # Makefile for automation
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Project dependencies
└── requirements-dev.txt          # Development dependencies
```

## Documentation

For more detailed documentation, see the `docs/` directory:

- [Architecture](docs/architecture.md)
- [Data Flow](docs/data_flow.md)
- [API](docs/api.md)
- [Deployment](docs/deployment.md)
- [Environment Variables](docs/environment_variables.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.