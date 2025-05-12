#!/usr/bin/env python
"""
Setup script for the LLM-Kafka Boilerplate.

This script helps set up a new project based on the boilerplate.
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Set up a new project based on the LLM-Kafka Boilerplate"
    )

    parser.add_argument("project_name", help="Name of the new project")

    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for the new project (default: current directory)",
    )

    parser.add_argument(
        "--author", default="Your Name", help="Author name for the new project"
    )

    parser.add_argument(
        "--email",
        default="your.email@example.com",
        help="Author email for the new project",
    )

    return parser.parse_args()


def create_project_directory(output_dir, project_name):
    """
    Create the project directory.

    Args:
        output_dir: Output directory
        project_name: Project name

    Returns:
        Path: Path to the project directory
    """
    # Convert project name to kebab case for directory name
    dir_name = re.sub(r"[^a-zA-Z0-9]", "-", project_name.lower())
    dir_name = re.sub(r"-+", "-", dir_name).strip("-")

    # Create the project directory
    project_dir = Path(output_dir) / dir_name
    if project_dir.exists():
        print(f"Error: Directory {project_dir} already exists")
        sys.exit(1)

    project_dir.mkdir(parents=True)
    print(f"Created project directory: {project_dir}")

    return project_dir


def copy_boilerplate(boilerplate_dir, project_dir):
    """
    Copy the boilerplate to the project directory.

    Args:
        boilerplate_dir: Boilerplate directory
        project_dir: Project directory
    """
    # Get the list of files and directories to copy
    items = os.listdir(boilerplate_dir)

    # Copy each item
    for item in items:
        src = os.path.join(boilerplate_dir, item)
        dst = os.path.join(project_dir, item)

        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    print(f"Copied boilerplate to {project_dir}")


def update_project_files(project_dir, project_name, author, email):
    """
    Update project files with the new project information.

    Args:
        project_dir: Project directory
        project_name: Project name
        author: Author name
        email: Author email
    """
    # Update pyproject.toml
    pyproject_path = os.path.join(project_dir, "pyproject.toml")
    if os.path.exists(pyproject_path):
        with open(pyproject_path, "r") as f:
            content = f.read()

        # Replace project name
        content = content.replace("llm-kafka-boilerplate", project_name.lower())
        content = content.replace("LLM-Kafka Boilerplate", project_name)

        # Replace author information
        content = content.replace("Your Name", author)
        content = content.replace("your.email@example.com", email)

        with open(pyproject_path, "w") as f:
            f.write(content)

        print(f"Updated {pyproject_path}")

    # Update README.md
    readme_path = os.path.join(project_dir, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()

        # Replace project name
        content = content.replace("LLM-Kafka Boilerplate", project_name)
        content = content.replace("llm-kafka-boilerplate", project_name.lower())

        with open(readme_path, "w") as f:
            f.write(content)

        print(f"Updated {readme_path}")

    # Update Dockerfile
    dockerfile_path = os.path.join(project_dir, "Dockerfile")
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path, "r") as f:
            content = f.read()

        # Replace project name in comments if needed
        content = content.replace("LLM-Kafka Boilerplate", project_name)

        with open(dockerfile_path, "w") as f:
            f.write(content)

        print(f"Updated {dockerfile_path}")

    # Update docker-compose.yml
    docker_compose_path = os.path.join(project_dir, "docker-compose.yml")
    if os.path.exists(docker_compose_path):
        with open(docker_compose_path, "r") as f:
            content = f.read()

        # Replace project name
        content = content.replace("llm-kafka-boilerplate", project_name.lower())

        with open(docker_compose_path, "w") as f:
            f.write(content)

        print(f"Updated {docker_compose_path}")


def main():
    """
    Main function.
    """
    # Parse command-line arguments
    args = parse_args()

    # Get the boilerplate directory
    boilerplate_dir = Path(__file__).parent.parent

    # Create the project directory
    project_dir = create_project_directory(args.output_dir, args.project_name)

    # Copy the boilerplate to the project directory
    copy_boilerplate(boilerplate_dir, project_dir)

    # Update project files
    update_project_files(project_dir, args.project_name, args.author, args.email)

    print(f"\nProject {args.project_name} created successfully!")
    print(f"To get started, run:")
    print(f"  cd {project_dir}")
    print(f"  pip install -r requirements.txt")
    print(f"  cp .env.example .env  # Then edit .env with your configuration")
    print(f"  python -m src")


if __name__ == "__main__":
    main()
