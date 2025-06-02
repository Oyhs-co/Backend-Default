# Pylance and Flake8 Fixes for TaskHub

I've identified and fixed several issues that were causing Pylance and Flake8 errors in your TaskHub project. Here's a summary of the changes and instructions on how to apply them.

## Main Issues Found

1. **Hyphens in Import Paths**: Python doesn't allow hyphens in module names, but your directory structure uses them (e.g., `api/auth-service`). This causes import errors.

2. **Relative Imports**: Some files use relative imports (e.g., `from schemas.user import ...`) which can cause issues when running the code from different directories.

3. **Missing Type Annotations**: Some functions are missing return type annotations, which Pylance flags as errors.

4. **Unused Imports**: There are unused imports in some files.

## Solutions Provided

I've created three scripts to help fix these issues:

1. **`fix_imports.py`**: Renames directories with hyphens to use underscores and updates import statements.
2. **`fix_linting.py`**: Fixes other common linting issues like relative imports, missing type annotations, etc.
3. **`LINTING_FIXES.md`**: A comprehensive guide on how to fix common Pylance and Flake8 issues.

I've also manually fixed some specific issues in:
- `api/shared/utils/supabase.py`
- `api/auth-service/app/services/auth_service.py`
- `api/notification-service/app/services/notification_service.py`

## How to Apply the Fixes

### Option 1: Run the Automated Scripts

1. Run the import fix script first:
   ```bash
   python fix_imports.py
   ```

2. Then run the linting fix script:
   ```bash
   python fix_linting.py
   ```

### Option 2: Apply the Changes Manually

If you prefer to make the changes manually, follow these steps:

1. **Rename Directories**:
   - Rename `api/api-gateway` to `api/api_gateway`
   - Rename `api/auth-service` to `api/auth_service`
   - Rename `api/document-service` to `api/document_service`
   - Rename `api/external-tools-service` to `api/external_tools_service`
   - Rename `api/notification-service` to `api/notification_service`
   - Rename `api/project-service` to `api/project_service`

2. **Update Import Statements**:
   - Replace `from api.api-gateway` with `from api.api_gateway`
   - Replace `from api.auth-service` with `from api.auth_service`
   - Replace `from api.document-service` with `from api.document_service`
   - Replace `from api.external-tools-service` with `from api.external_tools_service`
   - Replace `from api.notification-service` with `from api.notification_service`
   - Replace `from api.project-service` with `from api.project_service`

3. **Fix Relative Imports**:
   - Replace `from schemas.` with `from api.{service}.app.schemas.`
   - Replace `from services.` with `from api.{service}.app.services.`
   - Replace `from factories.` with `from api.{service}.app.factories.`
   - Replace `from decorators.` with `from api.{service}.app.decorators.`
   - Replace `from commands.` with `from api.{service}.app.commands.`
   - Replace `from observers.` with `from api.{service}.app.observers.`
   - Replace `from adapters.` with `from api.{service}.app.adapters.`

4. **Add Missing Type Annotations**:
   - Add return type annotations to functions
   - Add `from typing import Any` where needed

## Additional Recommendations

1. **Install Required Tools**:
   ```bash
   pip install black isort autoflake mypy flake8
   ```

2. **Configure VS Code**:
   Add these settings to your `.vscode/settings.json`:
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

3. **Add `__init__.py` Files**:
   Make sure all directories have an `__init__.py` file to make them proper Python packages.

4. **Set PYTHONPATH**:
   Set your PYTHONPATH to include the project root:
   ```bash
   export PYTHONPATH=/path/to/TaskHub:$PYTHONPATH
   ```

## Common Error Codes

### Flake8 Errors
- E501: Line too long
- F401: Imported but unused
- F403: 'from module import *' used
- E302: Expected 2 blank lines
- E305: Expected 2 blank lines after class or function definition

### Pylance Errors
- "Import 'module' could not be resolved"
- "Cannot import name 'X' from 'module'"
- "Type of 'parameter' is 'Any'"
- "Function is missing a return type annotation"

For more detailed information, please refer to the `LINTING_FIXES.md` file.