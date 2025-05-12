.PHONY: help install install-dev lint format test test-cov clean run docker-build docker-run

# Default target
help:
	@echo "Available targets:"
	@echo "  help        - Show this help message"
	@echo "  install     - Install production dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  lint        - Run linters (flake8, mypy)"
	@echo "  format      - Run formatters (black, isort)"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage report"
	@echo "  clean       - Remove build artifacts and cache files"
	@echo "  run         - Run the application"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run application in Docker container"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

# Run linters
lint:
	flake8 src tests
	mypy src tests

# Run formatters
format:
	black src tests
	isort src tests

# Run tests
test:
	pytest

# Run tests with coverage report
test-cov:
	pytest --cov=src --cov-report=term-missing --cov-report=html

# Clean build artifacts and cache files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Run the application
run:
	python -m src

# Build Docker image
docker-build:
	docker build -t llm-kafka-boilerplate .

# Run application in Docker container
docker-run:
	docker run --env-file .env llm-kafka-boilerplate