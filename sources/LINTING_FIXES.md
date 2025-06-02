# Fixing Pylance and Flake8 Issues in TaskHub

This document provides instructions on how to fix common Pylance and Flake8 issues in the TaskHub project.

## Common Issues

1. **Hyphens in Module Names**: Python doesn't allow hyphens in module names, but our directory structure uses them.
2. **Relative Imports**: Some files use relative imports which can cause issues.
3. **Missing Type Annotations**: Functions without return type annotations.
4. **Unused Imports**: Imports that are not used in the code.
5. **Line Length**: Lines exceeding the maximum length (usually 88 or 79 characters).
6. **Missing Docstrings**: Functions or classes without proper documentation.

## Automated Fixes

We've created two scripts to automatically fix most of these issues:

1. `fix_imports.py`: Renames directories with hyphens to use underscores and updates import statements.
2. `fix_linting.py`: Fixes other common linting issues like relative imports, missing type annotations, etc.

### Running the Scripts

1. First, run the import fix script:
   ```bash
   python fix_imports.py
   ```

2. Then, run the linting fix script:
   ```bash
   python fix_linting.py
   ```

### Required Tools

The linting fix script uses the following tools:
- Black: `pip install black`
- isort: `pip install isort`
- autoflake: `pip install autoflake`

## Manual Fixes

Some issues might require manual fixes:

### 1. Circular Imports

If you encounter circular import errors, you might need to:
- Move the import inside the function where it's used
- Restructure your code to avoid circular dependencies
- Use type hints with string literals (e.g., `def func() -> 'MyClass':`)

### 2. Type Annotation Issues

For complex type annotations:
```python
from typing import List, Dict, Any, Optional, Union, TypeVar, Generic

# For collections
items: List[str] = []
mapping: Dict[str, Any] = {}

# For optional values
name: Optional[str] = None

# For union types
value: Union[str, int] = "hello"
```

### 3. Fixing Module Not Found Errors

If you still get "module not found" errors after running the scripts:

1. Make sure your PYTHONPATH includes the project root:
   ```bash
   export PYTHONPATH=/path/to/TaskHub:$PYTHONPATH
   ```

2. Create empty `__init__.py` files in all directories to make them proper packages.

## IDE Configuration

### VS Code

1. Install the Python extension
2. Configure settings.json:
   ```json
   {
     "python.linting.enabled": true,
     "python.linting.flake8Enabled": true,
     "python.linting.pylintEnabled": false,
     "python.analysis.typeCheckingMode": "basic",
     "python.formatting.provider": "black",
     "editor.formatOnSave": true,
     "python.linting.flake8Args": [
       "--max-line-length=88",
       "--extend-ignore=E203"
     ],
     "python.sortImports.args": [
       "--profile", "black"
     ]
   }
   ```

### PyCharm

1. Go to Settings > Tools > Python Integrated Tools
2. Set Formatter to "Black"
3. Enable "Optimize imports on the fly"
4. Configure Flake8 as the linter

## Running Linters Manually

```bash
# Run Black formatter
black api/

# Sort imports
isort api/

# Run Flake8
flake8 api/

# Run MyPy for type checking
mypy api/
```

## Common Flake8 Error Codes

- E501: Line too long
- F401: Imported but unused
- F403: 'from module import *' used
- E302: Expected 2 blank lines
- E305: Expected 2 blank lines after class or function definition
- E231: Missing whitespace after ','
- E225: Missing whitespace around operator

## Common Pylance Error Messages

- "Import "module" could not be resolved"
- "Cannot import name 'X' from 'module'"
- "Type of "parameter" is "Any""
- "Function is missing a return type annotation"
- "Module has no attribute 'X'"