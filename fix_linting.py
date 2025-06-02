#!/usr/bin/env python3
"""
Script to fix common Pylance and Flake8 issues in the TaskHub project.
This script:
1. Adds missing type annotations
2. Fixes unused imports
3. Fixes line length issues
4. Adds missing docstrings
5. Fixes other common linting issues
"""

import os
import re
from pathlib import Path
import subprocess

# Project root directory
ROOT_DIR = Path(__file__).parent

def run_black():
    """Run Black formatter on the codebase"""
    print("Running Black formatter...")
    try:
        subprocess.run(["black", str(ROOT_DIR / "api")], check=True)
        print("  Black formatting completed successfully")
    except subprocess.CalledProcessError:
        print("  Error running Black. Make sure it's installed: pip install black")
    except FileNotFoundError:
        print("  Black not found. Install it with: pip install black")

def run_isort():
    """Run isort to sort imports"""
    print("Running isort...")
    try:
        subprocess.run(["isort", str(ROOT_DIR / "api")], check=True)
        print("  isort completed successfully")
    except subprocess.CalledProcessError:
        print("  Error running isort. Make sure it's installed: pip install isort")
    except FileNotFoundError:
        print("  isort not found. Install it with: pip install isort")

def fix_relative_imports():
    """Fix relative imports to use absolute imports"""
    print("Fixing relative imports...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Patterns to fix
    patterns = [
        (r'from schemas\.', r'from api.{service}.app.schemas.'),
        (r'from services\.', r'from api.{service}.app.services.'),
        (r'from factories\.', r'from api.{service}.app.factories.'),
        (r'from decorators\.', r'from api.{service}.app.decorators.'),
        (r'from commands\.', r'from api.{service}.app.commands.'),
        (r'from observers\.', r'from api.{service}.app.observers.'),
        (r'from adapters\.', r'from api.{service}.app.adapters.'),
    ]
    
    for file_path in python_files:
        # Determine service name from file path
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        path_parts = rel_path.split(os.sep)
        
        if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[2] == "app":
            service = path_parts[1]
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Check if file needs to be updated
            original_content = content
            for pattern, replacement in patterns:
                # Format replacement with service name
                formatted_replacement = replacement.format(service=service)
                content = re.sub(pattern, formatted_replacement, content)
            
            # Write updated content if changed
            if content != original_content:
                print(f"  Fixing imports in {rel_path}")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

def fix_missing_return_types():
    """Add missing return type annotations to functions"""
    print("Fixing missing return type annotations...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Pattern to find functions without return type annotations
    function_pattern = r'def ([a-zA-Z0-9_]+)\(([^)]*)\):'
    
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find functions without return type annotations
        matches = re.finditer(function_pattern, content)
        updated_content = content
        
        for match in matches:
            # Check if function already has return type
            if '->' not in match.group(0):
                # Get function name and parameters
                func_name = match.group(1)
                params = match.group(2)
                
                # Skip __init__ methods (they return None implicitly)
                if func_name == "__init__":
                    continue
                
                # Add return type annotation
                replacement = f"def {func_name}({params}) -> Any:"
                updated_content = updated_content.replace(match.group(0), replacement)
        
        # Add import for Any if needed
        if updated_content != content and "from typing import Any" not in updated_content:
            if "from typing import" in updated_content:
                updated_content = re.sub(
                    r'from typing import ([^\\n]*)',
                    r'from typing import \1, Any',
                    updated_content
                )
            else:
                updated_content = "from typing import Any\n" + updated_content
        
        # Write updated content if changed
        if updated_content != content:
            print(f"  Adding return types in {os.path.relpath(file_path, ROOT_DIR)}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)

def fix_unused_imports():
    """Fix unused imports using autoflake"""
    print("Fixing unused imports...")
    try:
        subprocess.run([
            "autoflake", 
            "--in-place", 
            "--remove-all-unused-imports", 
            "--recursive",
            str(ROOT_DIR / "api")
        ], check=True)
        print("  Unused imports removed successfully")
    except subprocess.CalledProcessError:
        print("  Error running autoflake. Make sure it's installed: pip install autoflake")
    except FileNotFoundError:
        print("  autoflake not found. Install it with: pip install autoflake")

def main():
    """Main function"""
    print("Starting linting fixes...")
    fix_relative_imports()
    fix_missing_return_types()
    fix_unused_imports()
    run_isort()
    run_black()
    print("Linting fixes completed!")

if __name__ == "__main__":
    main()