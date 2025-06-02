FROM python:3.12-slim

WORKDIR /app

# Set Python path
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.2

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --without dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Create necessary __init__.py files
RUN find /app/api -type d -exec touch {}/__init__.py \;

# Expose port
EXPOSE 8000

# Default command (will be overridden by docker-compose)
CMD ["python", "-m", "uvicorn", "api.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]