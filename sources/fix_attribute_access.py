#!/usr/bin/env python3
"""
Script to fix attribute access issues in the TaskHub project.
This script:
1. Adds safe attribute access for user.user_metadata
2. Adds type checking for JSON fields
3. Fixes other common attribute access issues
"""

import os
import re
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

def fix_user_metadata_access():
    """Fix user.user_metadata attribute access issues"""
    print("Fixing user.user_metadata attribute access issues...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Pattern to find user.user_metadata.get() calls
    pattern = r'(\w+)\.user_metadata\.get\(([^)]+)\)'
    
    # Process each file
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if file contains user.user_metadata
        if 'user_metadata' in content:
            # Find all user.user_metadata.get() calls
            matches = re.finditer(pattern, content)
            updated_content = content
            
            for match in matches:
                var_name = match.group(1)
                key = match.group(2)
                
                # Replace with safe access
                replacement = f'getattr({var_name}, "user_metadata", {{}}).get({key}, "")'
                updated_content = updated_content.replace(match.group(0), replacement)
            
            # Add safe access for direct attribute access
            direct_pattern = r'(\w+)\.user_metadata'
            direct_matches = re.finditer(direct_pattern, updated_content)
            
            for match in direct_matches:
                var_name = match.group(1)
                
                # Skip if it's already been fixed with getattr
                if f'getattr({var_name}, "user_metadata"' in updated_content:
                    continue
                
                # Replace with safe access
                replacement = f'getattr({var_name}, "user_metadata", {{}})'
                updated_content = updated_content.replace(match.group(0), replacement)
            
            # Write updated content if changed
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                
                print(f"  Fixed {os.path.relpath(file_path, ROOT_DIR)}")

def fix_json_field_access():
    """Fix JSON field attribute access issues"""
    print("Fixing JSON field attribute access issues...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # JSON fields in models
    json_fields = ['tags', 'metadata', 'details', 'channels', 'preferences_by_type']
    
    # Process each file
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        updated_content = content
        
        # Check for each JSON field
        for field in json_fields:
            # Pattern to find direct attribute access on JSON fields
            pattern = r'(\w+)\.' + field + r'(?!\s*=|\s*\()'
            
            # Find all matches
            matches = re.finditer(pattern, updated_content)
            
            for match in matches:
                var_name = match.group(1)
                
                # Skip if it's already been fixed
                if f'{var_name}.{field} or {{}}' in updated_content:
                    continue
                
                # Replace with safe access
                replacement = f'({var_name}.{field} or {{}})'
                updated_content = updated_content.replace(match.group(0), replacement)
        
        # Write updated content if changed
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            print(f"  Fixed {os.path.relpath(file_path, ROOT_DIR)}")

def main():
    """Main function"""
    print("Starting attribute access fixes...")
    fix_user_metadata_access()
    fix_json_field_access()
    print("Attribute access fixes completed!")

if __name__ == "__main__":
    main()