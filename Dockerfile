FROM python:3.13-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.2

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "api.api-gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]