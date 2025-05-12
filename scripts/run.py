#!/usr/bin/env python
"""
Script to run the LLM-Kafka Boilerplate application.

This script provides a command-line interface for running the application.
"""

import argparse
import logging
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import main


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Run the LLM-Kafka Boilerplate application"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--env-file", default=".env", help="Path to .env file (default: .env)"
    )

    return parser.parse_args()


def setup_environment(args):
    """
    Set up the environment based on command-line arguments.

    Args:
        args: Command-line arguments
    """
    # Set log level
    os.environ["LOG_LEVEL"] = args.log_level

    # Load environment variables from .env file
    if os.path.exists(args.env_file):
        print(f"Loading environment variables from {args.env_file}")
        with open(args.env_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                os.environ[key] = value
    else:
        print(f"Warning: .env file not found at {args.env_file}")


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()

    # Set up the environment
    setup_environment(args)

    # Run the application
    main()
