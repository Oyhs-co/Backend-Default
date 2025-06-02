#!/usr/bin/env python3
"""
Script to fix issues in main.py files across all services.
"""

import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

# Template for a basic main.py file
MAIN_PY_TEMPLATE = '''"""
{service_name} main module.
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="{service_title}",
    description="{service_description}",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Dict[str, str]: Health status
    """
    return {{"status": "healthy"}}


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint.

    Returns:
        Dict[str, str]: Service information
    """
    return {{
        "service": "{service_name}",
        "version": "1.0.0",
        "status": "running"
    }}
'''

def check_and_fix_main_files():
    """Check and fix main.py files in all services"""
    print("Checking and fixing main.py files...")
    
    services = [
        {
            "path": "api/auth_service/app/main.py",
            "name": "auth_service",
            "title": "TaskHub Auth Service",
            "description": "Authentication service for TaskHub platform"
        },
        {
            "path": "api/project_service/app/main.py",
            "name": "project_service",
            "title": "TaskHub Project Service",
            "description": "Project management service for TaskHub platform"
        },
        {
            "path": "api/document_service/app/main.py",
            "name": "document_service",
            "title": "TaskHub Document Service",
            "description": "Document management service for TaskHub platform"
        },
        {
            "path": "api/notification_service/app/main.py",
            "name": "notification_service",
            "title": "TaskHub Notification Service",
            "description": "Notification service for TaskHub platform"
        },
        {
            "path": "api/external_tools_service/app/main.py",
            "name": "external_tools_service",
            "title": "TaskHub External Tools Service",
            "description": "External tools integration service for TaskHub platform"
        }
    ]
    
    for service in services:
        file_path = ROOT_DIR / service["path"]
        
        # Check if file exists
        if not file_path.exists():
            print(f"  Creating {service['path']}...")
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create main.py with template
            content = MAIN_PY_TEMPLATE.format(
                service_name=service["name"],
                service_title=service["title"],
                service_description=service["description"]
            )
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"  Created {service['path']}")
        else:
            # Check if file has syntax errors
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Try to compile the file to check for syntax errors
                compile(content, file_path, 'exec')
                print(f"  {service['path']} - OK")
            except SyntaxError as e:
                print(f"  {service['path']} - Syntax error found: {e}")
                print(f"    Creating backup and replacing with template...")
                
                # Create backup
                backup_path = file_path.with_suffix('.py.bak')
                with open(backup_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                # Replace with template
                new_content = MAIN_PY_TEMPLATE.format(
                    service_name=service["name"],
                    service_title=service["title"],
                    service_description=service["description"]
                )
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"    Replaced with template. Original backed up to {backup_path}")

def fix_dockerfile():
    """Fix Dockerfile to ensure proper Python path"""
    print("Fixing Dockerfile...")
    
    dockerfile_path = ROOT_DIR / "Dockerfile"
    if dockerfile_path.exists():
        with open(dockerfile_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if PYTHONPATH is set correctly
        if 'ENV PYTHONPATH=/app' not in content:
            # Add PYTHONPATH after WORKDIR
            updated_content = content.replace(
                'WORKDIR /app',
                'WORKDIR /app\n\n# Set Python path\nENV PYTHONPATH=/app'
            )
        else:
            updated_content = content
        
        # Ensure we're using the correct Python version
        updated_content = updated_content.replace('FROM python:3.13-slim', 'FROM python:3.12-slim')
        
        # Write updated content if changed
        if updated_content != content:
            with open(dockerfile_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            print("  Updated Dockerfile")

def main():
    """Main function"""
    print("Starting main.py fixes...")
    check_and_fix_main_files()
    fix_dockerfile()
    print("Main.py fixes completed!")

if __name__ == "__main__":
    main()