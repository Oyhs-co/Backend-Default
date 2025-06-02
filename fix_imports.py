#!/usr/bin/env python3
"""
Script to fix import issues in the TaskHub project.
This script:
1. Renames directories with hyphens to use underscores
2. Updates import statements to use the new directory names
"""

import os
import re
import shutil
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

# Directories to rename (old_name -> new_name)
DIRS_TO_RENAME = {
    'api/api-gateway': 'api/api_gateway',
    'api/auth-service': 'api/auth_service',
    'api/document-service': 'api/document_service',
    'api/external-tools-service': 'api/external_tools_service',
    'api/notification-service': 'api/notification_service',
    'api/project-service': 'api/project_service',
}

# Import patterns to replace
IMPORT_PATTERNS = [
    (r'from api\.api-gateway', 'from api.api_gateway'),
    (r'from api\.auth-service', 'from api.auth_service'),
    (r'from api\.document-service', 'from api.document_service'),
    (r'from api\.external-tools-service', 'from api.external_tools_service'),
    (r'from api\.notification-service', 'from api.notification_service'),
    (r'from api\.project-service', 'from api.project_service'),
    (r'import api\.api-gateway', 'import api.api_gateway'),
    (r'import api\.auth-service', 'import api.auth_service'),
    (r'import api\.document-service', 'import api.document_service'),
    (r'import api\.external-tools-service', 'import api.external_tools_service'),
    (r'import api\.notification-service', 'import api.notification_service'),
    (r'import api\.project-service', 'import api.project_service'),
]

def rename_directories():
    """Rename directories with hyphens to use underscores"""
    print("Renaming directories...")
    for old_path, new_path in DIRS_TO_RENAME.items():
        old_full_path = ROOT_DIR / old_path
        new_full_path = ROOT_DIR / new_path
        
        if old_full_path.exists() and not new_full_path.exists():
            print(f"  Renaming {old_path} to {new_path}")
            # Create parent directory if it doesn't exist
            new_full_path.parent.mkdir(parents=True, exist_ok=True)
            # Move directory
            shutil.move(str(old_full_path), str(new_full_path))
        elif not old_full_path.exists() and new_full_path.exists():
            print(f"  Directory already renamed: {new_path}")
        elif not old_full_path.exists() and not new_full_path.exists():
            print(f"  Warning: Neither {old_path} nor {new_path} exists")

def update_imports():
    """Update import statements in Python files"""
    print("Updating import statements...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Update import statements in each file
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if file needs to be updated
        original_content = content
        for pattern, replacement in IMPORT_PATTERNS:
            content = re.sub(pattern, replacement, content)
        
        # Write updated content if changed
        if content != original_content:
            print(f"  Updating imports in {os.path.relpath(file_path, ROOT_DIR)}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

def update_docker_compose():
    """Update service names in docker-compose.yml"""
    print("Updating docker-compose.yml...")
    
    docker_compose_path = ROOT_DIR / 'docker-compose.yml'
    if docker_compose_path.exists():
        with open(docker_compose_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace service names
        for old_name, new_name in DIRS_TO_RENAME.items():
            old_service_name = old_name.split('/')[-1]
            new_service_name = new_name.split('/')[-1]
            content = content.replace(old_service_name, new_service_name)
        
        # Write updated content
        with open(docker_compose_path, 'w', encoding='utf-8') as file:
            file.write(content)

def main():
    """Main function"""
    print("Starting import fixes...")
    rename_directories()
    update_imports()
    update_docker_compose()
    print("Import fixes completed!")

if __name__ == "__main__":
    main()