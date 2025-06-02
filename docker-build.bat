@echo off
setlocal

REM Check if Python 3.13 image is available
docker pull python:3.13-slim >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using Python 3.13 image
    REM No changes needed to Dockerfile
) else (
    echo Python 3.13 image not available, falling back to Python 3.12
    REM Update Dockerfile to use Python 3.12
    powershell -Command "(Get-Content Dockerfile) -replace 'FROM python:3.13-slim', 'FROM python:3.12-slim' | Set-Content Dockerfile"
)

REM Build and run the Docker Compose setup
docker-compose build
docker-compose up

endlocal