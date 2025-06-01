from functools import wraps
from typing import Callable, Any, Dict
from sqlalchemy.orm import Session

from api.shared.models.document import Document
from api.shared.exceptions.document_exceptions import (
    DocumentNotFoundException,
    InsufficientDocumentPermissionException
)


def document_exists(func: Callable) -> Callable:
    """
    Decorator to check if document exists.
    
    Args:
        func (Callable): Function to decorate
        
    Returns:
        Callable: Decorated function
    """
    @wraps(func)
    def wrapper(self, document_id: str, *args, **kwargs):
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()
        
        # Check if document exists
        if not document:
            raise DocumentNotFoundException()
        
        # Call function
        return func(self, document_id, *args, **kwargs)
    
    return wrapper


def require_permission(permission_type: str) -> Callable:
    """
    Decorator to check if user has permission.
    
    Args:
        permission_type (str): Permission type ('view', 'edit', 'delete', 'share')
        
    Returns:
        Callable: Decorator
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, document_id: str, user_id: str, *args, **kwargs):
            # Check if user has permission
            if not self._has_permission(document_id, user_id, permission_type):
                raise InsufficientDocumentPermissionException(
                    f"User does not have permission to {permission_type} this document"
                )
            
            # Call function
            return func(self, document_id, user_id, *args, **kwargs)
        
        return wrapper
    
    return decorator


def log_document_activity(action: str) -> Callable:
    """
    Decorator to log document activity.
    
    Args:
        action (str): Activity action
        
    Returns:
        Callable: Decorator
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, document_id: str, user_id: str, *args, **kwargs):
            # Get document
            document = self.db.query(Document).filter(Document.id == document_id).first()
            
            # Call function
            result = func(self, document_id, user_id, *args, **kwargs)
            
            # Log activity
            if document:
                from api.project-service.app.services.activity_service import ActivityService
                
                activity_service = ActivityService(self.db)
                activity_service.log_activity(
                    project_id=document.project_id,
                    user_id=user_id,
                    action=action,
                    entity_type="document",
                    entity_id=document_id,
                    details={"name": document.name}
                )
            
            # Return result
            return result
        
        return wrapper
    
    return decorator


def cache_document(func: Callable) -> Callable:
    """
    Decorator to cache document.
    
    Args:
        func (Callable): Function to decorate
        
    Returns:
        Callable: Decorated function
    """
    # This is a placeholder for a real caching implementation
    # In a real application, you would use Redis or another caching solution
    cache: Dict[str, Any] = {}
    
    @wraps(func)
    def wrapper(self, document_id: str, *args, **kwargs):
        # Check if document is in cache
        cache_key = f"document:{document_id}"
        if cache_key in cache:
            return cache[cache_key]
        
        # Call function
        result = func(self, document_id, *args, **kwargs)
        
        # Cache result
        cache[cache_key] = result
        
        # Return result
        return result
    
    return wrapper