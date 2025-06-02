# Docker Build Fixes for TaskHub

This document provides instructions on how to fix Docker build issues in the TaskHub project.

## Issues Fixed

1. **Duplicate `[tool.poetry]` Section in pyproject.toml**:
   - The error `Cannot declare ('tool', 'poetry') twice` was caused by having two `[tool.poetry]` sections in the pyproject.toml file.
   - Fixed by merging the two sections into one.

2. **Python Version Compatibility**:
   - Updated the Dockerfile to use Python 3.13 to match the project requirements.
   - Added fallback scripts to use Python 3.12 if 3.13 is not available.

3. **Database URL Format**:
   - Fixed the DATABASE_URL format in docker-compose.yml to include the proper protocol prefix (`postgresql://`).

## How to Build and Run

### Option 1: Using the Provided Scripts

For Linux/macOS:
```bash
chmod +x docker-build.sh
./docker-build.sh
```

For Windows:
```bash
docker-build.bat
```

These scripts will:
1. Check if Python 3.13 is available and fall back to 3.12 if needed
2. Build the Docker images
3. Start the Docker Compose setup

### Option 2: Manual Build

1. Make sure you have a `.env` file with the required environment variables (copy from `.env.example`):
   ```bash
   cp .env.example .env
   # Edit .env to add your actual values
   ```

2. Build and run the Docker Compose setup:
   ```bash
   docker-compose build
   docker-compose up
   ```

## Troubleshooting

If you encounter any issues during the build process, try the following:

1. **Poetry Version Issues**:
   - Make sure you're using Poetry 1.8.2 or later
   - If you get errors with Poetry, try updating the Poetry version in the Dockerfile

2. **Python Version Issues**:
   - If Python 3.13 is not available, modify the Dockerfile to use Python 3.12:
     ```
     FROM python:3.12-slim
     ```

3. **Dependencies Installation Issues**:
   - If you encounter issues with dependencies, try running:
     ```bash
     docker-compose build --no-cache
     ```

4. **Database Connection Issues**:
   - Make sure your DATABASE_URL is correctly formatted
   - Ensure your database is accessible from the Docker containers

## Environment Variables

Make sure to set the following environment variables in your `.env` file:

- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `SUPABASE_URL`: Your Supabase URL
- `SUPABASE_KEY`: Your Supabase API key
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`: Email service configuration
- `PUSH_API_KEY`, `PUSH_API_URL`: Push notification service configuration
- `SMS_API_KEY`, `SMS_API_URL`: SMS service configuration

## Service URLs

The services will be available at:

- API Gateway: http://localhost:8000
- Auth Service: http://localhost:8001
- Project Service: http://localhost:8002
- Document Service: http://localhost:8003
- Notification Service: http://localhost:8004
- External Tools Service: http://localhost:8005
- RabbitMQ Management: http://localhost:15672 (guest/guest)