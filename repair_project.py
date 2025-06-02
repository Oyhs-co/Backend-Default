#!/usr/bin/env python3
"""
Complete repair script for the TaskHub project.
This script will fix all known issues and prepare the project for running.
"""

import os
import sys
import subprocess
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

def run_command(command, description):
    """Run a command and show the result"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {description} completed successfully")
            return True
        else:
            print(f"  ❌ {description} failed")
            if result.stderr:
                print(f"     Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ {description} failed: {e}")
        return False

def main():
    """Main function"""
    print("TaskHub Project Repair Script")
    print("=" * 50)
    
    # Step 1: Run all fix scripts
    print("\nStep 1: Running fix scripts...")
    
    scripts = [
        ("python fix_imports.py", "Fixing import issues"),
        ("python fix_datetime_utcnow.py", "Fixing datetime.utcnow() deprecation"),
        ("python fix_attribute_access.py", "Fixing attribute access issues"),
        ("python fix_syntax_errors.py", "Fixing syntax errors"),
        ("python fix_main_files.py", "Fixing main.py files"),
    ]
    
    for script, description in scripts:
        if os.path.exists(script.split()[1]):
            run_command(script, description)
    
    # Step 2: Create .env file if it doesn't exist
    print("\nStep 2: Checking environment configuration...")
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("  Creating .env file from .env.example...")
        import shutil
        shutil.copy(env_example, env_file)
        print("  ✓ .env file created. Please update it with your actual values.")
    elif env_file.exists():
        print("  ✓ .env file already exists")
    
    # Step 3: Run diagnostics
    print("\nStep 3: Running diagnostics...")
    run_command("python diagnose.py", "Running diagnostics")
    
    # Step 4: Build Docker images
    print("\nStep 4: Building Docker images...")
    if run_command("docker-compose build --no-cache", "Building Docker images"):
        print("\n" + "=" * 50)
        print("✓ Project repair completed!")
        print("\nYou can now run the project with:")
        print("  docker-compose up")
        print("\nOr run individual services:")
        print("  docker-compose up api_gateway")
        print("  docker-compose up auth_service")
        print("  etc.")
    else:
        print("\n" + "=" * 50)
        print("❌ Docker build failed. Please check the errors above.")
        print("\nTroubleshooting tips:")
        print("1. Make sure Docker is running")
        print("2. Check if you have enough disk space")
        print("3. Try running: docker system prune -a")
        print("4. Check the Dockerfile and docker-compose.yml for issues")

if __name__ == "__main__":
    main()