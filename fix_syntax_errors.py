#!/usr/bin/env python3
"""
Script to fix syntax errors in the TaskHub project.
This script:
1. Fixes type annotations in async functions
2. Fixes missing return type annotations
3. Fixes import issues
"""

import os
import re
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

def fix_async_function_annotations():
    """Fix type annotations in async functions"""
    print("Fixing async function type annotations...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Pattern to find async functions with problematic annotations
    pattern = r'async def (\w+)\([^)]*\)(\s*->\s*[^:]+)?:'
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Skip if file is empty
            if not content.strip():
                continue
                
            # Check for syntax issues in async functions
            updated_content = content
            
            # Fix missing return type annotations for async functions
            def fix_return_annotation(match):
                func_name = match.group(1)
                return_type = match.group(2)
                
                # If no return type, add -> Any
                if not return_type:
                    return match.group(0).replace(':', ' -> Any:')
                return match.group(0)
            
            updated_content = re.sub(pattern, fix_return_annotation, updated_content)
            
            # Write updated content if changed
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                print(f"  Fixed {os.path.relpath(file_path, ROOT_DIR)}")
                
        except Exception as e:
            print(f"  Error processing {os.path.relpath(file_path, ROOT_DIR)}: {e}")

def fix_import_issues():
    """Fix import issues in the codebase"""
    print("Fixing import issues...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Skip if file is empty
            if not content.strip():
                continue
                
            updated_content = content
            
            # Add missing imports for Any type
            if ' -> Any:' in updated_content and 'from typing import' in updated_content:
                if 'Any' not in updated_content:
                    # Find the typing import line
                    typing_import_match = re.search(r'from typing import ([^\n]+)', updated_content)
                    if typing_import_match:
                        imports = typing_import_match.group(1)
                        if 'Any' not in imports:
                            new_imports = imports.rstrip() + ', Any'
                            updated_content = updated_content.replace(
                                f'from typing import {imports}',
                                f'from typing import {new_imports}'
                            )
            
            # Write updated content if changed
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                print(f"  Fixed imports in {os.path.relpath(file_path, ROOT_DIR)}")
                
        except Exception as e:
            print(f"  Error processing {os.path.relpath(file_path, ROOT_DIR)}: {e}")

def fix_uvicorn_command():
    """Fix uvicorn command syntax in docker-compose.yml"""
    print("Fixing uvicorn commands...")
    
    docker_compose_path = ROOT_DIR / "docker-compose.yml"
    if docker_compose_path.exists():
        with open(docker_compose_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Fix uvicorn commands to use proper module paths
        updated_content = content
        
        # Update uvicorn commands
        uvicorn_commands = [
            ('uvicorn api.api_gateway.main:app', 'python -m uvicorn api.api_gateway.main:app'),
            ('uvicorn api.auth_service.app.main:app', 'python -m uvicorn api.auth_service.app.main:app'),
            ('uvicorn api.project_service.app.main:app', 'python -m uvicorn api.project_service.app.main:app'),
            ('uvicorn api.document_service.app.main:app', 'python -m uvicorn api.document_service.app.main:app'),
            ('uvicorn api.notification_service.app.main:app', 'python -m uvicorn api.notification_service.app.main:app'),
            ('uvicorn api.external_tools_service.app.main:app', 'python -m uvicorn api.external_tools_service.app.main:app'),
        ]
        
        for old_cmd, new_cmd in uvicorn_commands:
            updated_content = updated_content.replace(old_cmd, new_cmd)
        
        # Write updated content if changed
        if updated_content != content:
            with open(docker_compose_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            print("  Fixed uvicorn commands in docker-compose.yml")

def create_missing_init_files():
    """Create missing __init__.py files"""
    print("Creating missing __init__.py files...")
    
    # Walk through all directories in api
    for root, dirs, files in os.walk(ROOT_DIR / "api"):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        # Check if __init__.py exists
        init_file = os.path.join(root, '__init__.py')
        if not os.path.exists(init_file):
            # Create empty __init__.py
            with open(init_file, 'w', encoding='utf-8') as file:
                file.write('"""Package initialization."""\n')
            print(f"  Created {os.path.relpath(init_file, ROOT_DIR)}")

def main():
    """Main function"""
    print("Starting syntax error fixes...")
    create_missing_init_files()
    fix_async_function_annotations()
    fix_import_issues()
    fix_uvicorn_command()
    print("Syntax error fixes completed!")

if __name__ == "__main__":
    main()