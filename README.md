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

## Creating New Projects from the Boilerplate

There are multiple ways to create a new project using this boilerplate:

### 1. Using GitHub Template

If the repository is set up as a template on GitHub:

1. Navigate to the GitHub repository page
2. Click the "Use this template" button
3. Select "Create a new repository"
4. Fill in your repository details and click "Create repository from template"
5. Clone your new repository:
   ```bash
   git clone https://github.com/dannykellett/your-new-project.git
   cd your-new-project
   ```
6. Update project information in `pyproject.toml`, `README.md`, and other files

### 2. Using the Setup Script

The boilerplate includes a setup script that automates the process of creating a new project:

1. Clone the boilerplate repository:
   ```bash
   git clone https://github.com/dannykellett/llm-kafka-boilerplate.git
   ```

2. Run the setup script:
   ```bash
   cd llm-kafka-boilerplate
   python boilerplate/scripts/setup.py "Your Project Name" --output-dir /path/to/output --author "Your Name" --email "your.email@example.com"
   ```

   Arguments:
   - `project_name` (required): Name of your new project
   - `--output-dir` (optional): Output directory (default: current directory)
   - `--author` (optional): Author name for the project
   - `--email` (optional): Author email for the project

3. Navigate to your new project directory and initialize git:
   ```bash
   cd /path/to/output/your-project-name
   git init
   git add .
   git commit -m "Initial commit from boilerplate"
   ```

### 3. Manual Copy

You can also manually copy the boilerplate:

1. Clone the repository:
   ```bash
   git clone https://github.com/dannykellett/llm-kafka-boilerplate.git
   ```

2. Create a new directory for your project:
   ```bash
   mkdir /path/to/your-new-project
   ```

3. Copy the boilerplate files:
   ```bash
   cp -r llm-kafka-boilerplate/* /path/to/your-new-project/
   ```

4. Update project information in `pyproject.toml`, `README.md`, and other files

### Installation

After creating your project using one of the methods above:

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

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

First, ensure you've installed the package in development mode:

```bash
# Install in development mode
make install-dev
```

Then you can run the application using one of these methods:

```bash
# Run using the Makefile (recommended)
make run

# Run as a Python module
python -m src

# Or using Docker
make docker-build
make docker-run
```

> **Note:** Do not run the application directly with `python src/app.py` or `uv run src/app.py` as this will cause import errors. The application uses absolute imports and must be installed in development mode or run as a module.

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

## Development Guidelines

This project follows a set of comprehensive coding standards and best practices. All contributors should adhere to these guidelines:

- [Python Coding Rules](python_coding_rules.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
