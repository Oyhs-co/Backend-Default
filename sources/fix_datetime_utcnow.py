#!/usr/bin/env python3
"""
Script to fix datetime.utcnow() deprecation warnings in the TaskHub project.
This script:
1. Replaces all instances of datetime.utcnow() with datetime.now(timezone.utc)
2. Adds the necessary timezone import if it's missing
"""

import os
import re
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

def fix_datetime_utcnow():
    """Replace datetime.utcnow() with datetime.now(timezone.utc)"""
    print("Fixing datetime.utcnow() deprecation warnings...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Process each file
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if file contains datetime.utcnow()
        if 'datetime.utcnow()' in content:
            # Check if timezone is already imported
            has_timezone_import = re.search(r'from\s+datetime\s+import\s+.*timezone', content) is not None
            
            # Replace datetime.utcnow() with datetime.now(timezone.utc)
            updated_content = content.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')
            
            # Add timezone import if needed
            if not has_timezone_import:
                # Find the datetime import line
                datetime_import_match = re.search(r'from\s+datetime\s+import\s+([^\n]+)', updated_content)
                if datetime_import_match:
                    # Add timezone to the existing import
                    import_line = datetime_import_match.group(0)
                    if import_line.endswith(','):
                        new_import_line = import_line + ' timezone'
                    else:
                        new_import_line = import_line + ', timezone'
                    updated_content = updated_content.replace(import_line, new_import_line)
                else:
                    # Add a new import line
                    updated_content = 'from datetime import datetime, timezone\n' + updated_content
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            print(f"  Fixed {os.path.relpath(file_path, ROOT_DIR)}")

def fix_fromtimestamp():
    """Add timezone to datetime.fromtimestamp() calls"""
    print("Fixing datetime.fromtimestamp() timezone warnings...")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(ROOT_DIR / "api"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Process each file
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if file contains datetime.fromtimestamp()
        if 'datetime.fromtimestamp(' in content and 'timezone.utc' not in content:
            # Check if timezone is already imported
            has_timezone_import = re.search(r'from\s+datetime\s+import\s+.*timezone', content) is not None
            
            # Replace datetime.fromtimestamp(exp) with datetime.fromtimestamp(exp, tz=timezone.utc)
            updated_content = re.sub(
                r'datetime\.fromtimestamp\(([^)]+)\)', 
                r'datetime.fromtimestamp(\1, tz=timezone.utc)', 
                content
            )
            
            # Add timezone import if needed
            if not has_timezone_import:
                # Find the datetime import line
                datetime_import_match = re.search(r'from\s+datetime\s+import\s+([^\n]+)', updated_content)
                if datetime_import_match:
                    # Add timezone to the existing import
                    import_line = datetime_import_match.group(0)
                    if import_line.endswith(','):
                        new_import_line = import_line + ' timezone'
                    else:
                        new_import_line = import_line + ', timezone'
                    updated_content = updated_content.replace(import_line, new_import_line)
                else:
                    # Add a new import line
                    updated_content = 'from datetime import datetime, timezone\n' + updated_content
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            print(f"  Fixed {os.path.relpath(file_path, ROOT_DIR)}")

def main():
    """Main function"""
    print("Starting datetime fixes...")
    fix_datetime_utcnow()
    fix_fromtimestamp()
    print("Datetime fixes completed!")

if __name__ == "__main__":
    main()