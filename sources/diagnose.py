#!/usr/bin/env python3
"""
Script to diagnose issues in the TaskHub project.
"""

import os
import sys
import subprocess
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print("  ⚠️  Warning: Python 3.12+ is recommended")
    else:
        print("  ✓ Python version is OK")

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\nChecking dependencies...")
    try:
        import fastapi
        print("  ✓ FastAPI is installed")
    except ImportError:
        print("  ❌ FastAPI is not installed")
    
    try:
        import uvicorn
        print("  ✓ Uvicorn is installed")
    except ImportError:
        print("  ❌ Uvicorn is not installed")
    
    try:
        import sqlalchemy
        print("  ✓ SQLAlchemy is installed")
    except ImportError:
        print("  ❌ SQLAlchemy is not installed")
    
    try:
        import supabase
        print("  ✓ Supabase is installed")
    except ImportError:
        print("  ❌ Supabase is not installed")

def check_file_structure():
    """Check if all required files exist"""
    print("\nChecking file structure...")
    
    required_files = [
        "api/__init__.py",
        "api/api_gateway/__init__.py",
        "api/api_gateway/main.py",
        "api/auth_service/__init__.py",
        "api/auth_service/app/__init__.py",
        "api/auth_service/app/main.py",
        "api/project_service/__init__.py",
        "api/project_service/app/__init__.py",
        "api/project_service/app/main.py",
        "api/document_service/__init__.py",
        "api/document_service/app/__init__.py",
        "api/document_service/app/main.py",
        "api/notification_service/__init__.py",
        "api/notification_service/app/__init__.py",
        "api/notification_service/app/main.py",
        "api/external_tools_service/__init__.py",
        "api/external_tools_service/app/__init__.py",
        "api/external_tools_service/app/main.py",
        "api/shared/__init__.py",
        "api/shared/utils/__init__.py",
        "api/shared/models/__init__.py",
        "api/shared/exceptions/__init__.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = ROOT_DIR / file_path
        if not full_path.exists():
            missing_files.append(file_path)
            print(f"  ❌ Missing: {file_path}")
        else:
            print(f"  ✓ Found: {file_path}")
    
    return missing_files

def check_syntax_errors():
    """Check for syntax errors in Python files"""
    print("\nChecking for syntax errors...")
    
    error_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    compile(content, file_path, 'exec')
                except SyntaxError as e:
                    error_files.append((file_path, str(e)))
                    print(f"  ❌ Syntax error in {os.path.relpath(file_path, ROOT_DIR)}: {e}")
    
    if not error_files:
        print("  ✓ No syntax errors found")
    
    return error_files

def test_imports():
    """Test if services can be imported"""
    print("\nTesting imports...")
    
    # Add project root to Python path
    sys.path.insert(0, str(ROOT_DIR))
    
    services = [
        "api.api_gateway.main",
        "api.auth_service.app.main",
        "api.project_service.app.main",
        "api.document_service.app.main",
        "api.notification_service.app.main",
        "api.external_tools_service.app.main",
    ]
    
    for service in services:
        try:
            __import__(service)
            print(f"  ✓ Can import {service}")
        except Exception as e:
            print(f"  ❌ Cannot import {service}: {e}")

def check_env_file():
    """Check if .env file exists"""
    print("\nChecking environment configuration...")
    
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    
    if env_file.exists():
        print("  ✓ .env file exists")
    else:
        print("  ❌ .env file not found")
        if env_example.exists():
            print("    ℹ️  Copy .env.example to .env and configure it")

def main():
    """Main function"""
    print("TaskHub Project Diagnostics")
    print("=" * 50)
    
    check_python_version()
    check_dependencies()
    missing_files = check_file_structure()
    syntax_errors = check_syntax_errors()
    check_env_file()
    test_imports()
    
    print("\n" + "=" * 50)
    print("Summary:")
    
    if missing_files:
        print(f"  ❌ {len(missing_files)} missing files")
        print("     Run: python fix_syntax_errors.py")
    
    if syntax_errors:
        print(f"  ❌ {len(syntax_errors)} files with syntax errors")
        print("     Run: python fix_main_files.py")
    
    if not missing_files and not syntax_errors:
        print("  ✓ All checks passed!")
        print("\nYou can now run:")
        print("  docker-compose build")
        print("  docker-compose up")

if __name__ == "__main__":
    main()