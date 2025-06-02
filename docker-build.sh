#!/bin/bash

# Check if Python 3.13 image is available
if docker pull python:3.13-slim &>/dev/null; then
    echo "Using Python 3.13 image"
    # No changes needed to Dockerfile
else
    echo "Python 3.13 image not available, falling back to Python 3.12"
    # Update Dockerfile to use Python 3.12
    sed -i 's/FROM python:3.13-slim/FROM python:3.12-slim/' Dockerfile
fi

# Build and run the Docker Compose setup
docker-compose build
docker-compose up