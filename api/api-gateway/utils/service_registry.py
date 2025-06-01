import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
PROJECT_SERVICE_URL = os.getenv("PROJECT_SERVICE_URL", "http://localhost:8002")
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://localhost:8003")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8004")
EXTERNAL_TOOLS_SERVICE_URL = os.getenv("EXTERNAL_TOOLS_SERVICE_URL", "http://localhost:8005")


class ServiceRegistry:
    """Registry for microservices"""
    
    def __init__(self):
        """Initialize ServiceRegistry"""
        self.services = {
            "auth": {
                "url": AUTH_SERVICE_URL,
                "routes": [
                    {"path": "/auth/register", "methods": ["POST"]},
                    {"path": "/auth/login", "methods": ["POST"]},
                    {"path": "/auth/validate", "methods": ["GET"]},
                    {"path": "/auth/refresh", "methods": ["POST"]},
                    {"path": "/auth/logout", "methods": ["POST"]},
                    {"path": "/auth/profile", "methods": ["GET"]},
                    {"path": "/health", "methods": ["GET"]}
                ]
            },
            "projects": {
                "url": PROJECT_SERVICE_URL,
                "routes": [
                    {"path": "/projects", "methods": ["GET", "POST"]},
                    {"path": "/projects/{project_id}", "methods": ["GET", "PUT", "DELETE"]},
                    {"path": "/projects/{project_id}/members", "methods": ["GET", "POST"]},
                    {"path": "/projects/{project_id}/members/{member_id}", "methods": ["PUT", "DELETE"]},
                    {"path": "/projects/{project_id}/tasks", "methods": ["GET", "POST"]},
                    {"path": "/projects/{project_id}/tasks/{task_id}", "methods": ["GET", "PUT", "DELETE"]},
                    {"path": "/projects/{project_id}/tasks/{task_id}/comments", "methods": ["GET", "POST"]},
                    {"path": "/projects/{project_id}/activities", "methods": ["GET"]},
                    {"path": "/projects/{project_id}/tasks/{task_id}/assign", "methods": ["POST"]},
                    {"path": "/projects/{project_id}/tasks/{task_id}/status", "methods": ["POST"]},
                    {"path": "/projects/{project_id}/tasks/{task_id}/undo", "methods": ["POST"]},
                    {"path": "/projects/{project_id}/tasks/{task_id}/redo", "methods": ["POST"]},
                    {"path": "/health", "methods": ["GET"]}
                ]
            },
            "documents": {
                "url": DOCUMENT_SERVICE_URL,
                "routes": [
                    {"path": "/documents", "methods": ["POST"]},
                    {"path": "/documents/{document_id}", "methods": ["GET", "PUT", "DELETE"]},
                    {"path": "/projects/{project_id}/documents", "methods": ["GET"]},
                    {"path": "/documents/upload", "methods": ["POST"]},
                    {"path": "/documents/{document_id}/versions", "methods": ["GET", "POST"]},
                    {"path": "/documents/{document_id}/versions/{version}", "methods": ["GET"]},
                    {"path": "/documents/{document_id}/permissions", "methods": ["GET", "POST"]},
                    {"path": "/documents/{document_id}/permissions/{permission_id}", "methods": ["PUT", "DELETE"]},
                    {"path": "/health", "methods": ["GET"]}
                ]
            },
            "notifications": {
                "url": NOTIFICATION_SERVICE_URL,
                "routes": [
                    {"path": "/notifications", "methods": ["GET", "POST"]},
                    {"path": "/notifications/batch", "methods": ["POST"]},
                    {"path": "/notifications/unread", "methods": ["GET"]},
                    {"path": "/notifications/{notification_id}/read", "methods": ["PUT"]},
                    {"path": "/notifications/read-all", "methods": ["PUT"]},
                    {"path": "/notifications/{notification_id}", "methods": ["DELETE"]},
                    {"path": "/notification-preferences", "methods": ["GET", "PUT"]},
                    {"path": "/health", "methods": ["GET"]}
                ]
            },
            "external-tools": {
                "url": EXTERNAL_TOOLS_SERVICE_URL,
                "routes": [
                    {"path": "/oauth/providers", "methods": ["GET"]},
                    {"path": "/oauth/providers/{provider_id}", "methods": ["GET"]},
                    {"path": "/oauth/authorize", "methods": ["POST"]},
                    {"path": "/oauth/callback", "methods": ["POST"]},
                    {"path": "/connections", "methods": ["GET", "POST"]},
                    {"path": "/connections/{connection_id}", "methods": ["GET", "DELETE"]},
                    {"path": "/connections/{connection_id}/refresh", "methods": ["POST"]},
                    {"path": "/connections/{connection_id}/revoke", "methods": ["POST"]},
                    {"path": "/health", "methods": ["GET"]}
                ]
            }
        }
    
    def get_service_url(self, service_name: str) -> str:
        """
        Get service URL.
        
        Args:
            service_name (str): Service name
            
        Returns:
            str: Service URL
            
        Raises:
            ValueError: If service not found
        """
        service = self.services.get(service_name)
        
        if not service:
            raise ValueError(f"Service {service_name} not found")
        
        return service["url"]
    
    def get_service_for_path(self, path: str, method: str) -> Dict[str, Any]:
        """
        Get service for a path and method.
        
        Args:
            path (str): Request path
            method (str): HTTP method
            
        Returns:
            Dict[str, Any]: Service information
            
        Raises:
            ValueError: If service not found for path and method
        """
        # Extract service name from path
        path_parts = path.strip("/").split("/")
        service_name = path_parts[0] if path_parts else ""
        
        # Special case for auth service
        if service_name == "auth":
            return {
                "name": "auth",
                "url": self.get_service_url("auth")
            }
        
        # Check all services for matching route
        for name, service in self.services.items():
            for route in service["routes"]:
                if self._match_route(path, route["path"]) and method in route["methods"]:
                    return {
                        "name": name,
                        "url": service["url"]
                    }
        
        raise ValueError(f"No service found for path {path} and method {method}")
    
    def _match_route(self, path: str, route_path: str) -> bool:
        """
        Check if a path matches a route path.
        
        Args:
            path (str): Request path
            route_path (str): Route path
            
        Returns:
            bool: True if path matches route path, False otherwise
        """
        # Split paths into parts
        path_parts = path.strip("/").split("/")
        route_parts = route_path.strip("/").split("/")
        
        # Check if number of parts match
        if len(path_parts) != len(route_parts):
            return False
        
        # Check if parts match
        for i, route_part in enumerate(route_parts):
            # If route part is a parameter (e.g., {project_id}), it matches any value
            if route_part.startswith("{") and route_part.endswith("}"):
                continue
            
            # Otherwise, parts must match exactly
            if route_part != path_parts[i]:
                return False
        
        return True
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """
        Get all services.
        
        Returns:
            List[Dict[str, Any]]: List of services
        """
        return [
            {
                "name": name,
                "url": service["url"],
                "routes": service["routes"]
            }
            for name, service in self.services.items()
        ]


# Create global service registry
service_registry = ServiceRegistry()