FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy pyproject.toml first for better caching
COPY pyproject.toml .
RUN uv pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Run the application
CMD ["python", "-m", "src"]