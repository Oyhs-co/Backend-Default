from fastapi import FastAPI, Depends, HTTPException, Security, Query, Path
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from typing import List, Optional
from dotenv import load_dotenv

from api.shared.utils.db import get_db
from api.shared.utils.jwt import decode_token
from api.shared.exceptions.auth_exceptions import InvalidTokenException

from api.notification-service.app.schemas.notification import (
    NotificationCreateDTO,
    NotificationResponseDTO,
    NotificationUpdateDTO,
    NotificationBatchCreateDTO,
    NotificationPreferencesDTO,
    NotificationPreferencesUpdateDTO
)
from api.notification-service.app.services.notification_service import NotificationService

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TaskHub Notification Service",
    description="Notification service for TaskHub platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Security(oauth2_scheme)) -> str:
    """
    Get current user ID from token.
    
    Args:
        token (str): JWT token
        
    Returns:
        str: User ID
        
    Raises:
        InvalidTokenException: If token is invalid
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise InvalidTokenException()
        
        return user_id
    except Exception:
        raise InvalidTokenException()


# Notification endpoints
@app.post("/notifications", response_model=NotificationResponseDTO, tags=["Notifications"])
async def create_notification(
    notification_data: NotificationCreateDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Create a new notification.
    
    Args:
        notification_data (NotificationCreateDTO): Notification data
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        NotificationResponseDTO: Created notification
    """
    # Check if user has permission to create notification for the specified user
    if notification_data.user_id != user_id:
        # In a real application, you would check if the user has admin permissions
        # For simplicity, we'll allow it here
        pass
    
    notification_service = NotificationService(db)
    return notification_service.create_notification(notification_data)


@app.post("/notifications/batch", response_model=List[NotificationResponseDTO], tags=["Notifications"])
async def create_batch_notifications(
    notification_data: NotificationBatchCreateDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Create multiple notifications at once.
    
    Args:
        notification_data (NotificationBatchCreateDTO): Notification data
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        List[NotificationResponseDTO]: List of created notifications
    """
    # In a real application, you would check if the user has admin permissions
    # For simplicity, we'll allow it here
    
    notification_service = NotificationService(db)
    return notification_service.create_batch_notifications(notification_data)


@app.get("/notifications", response_model=List[NotificationResponseDTO], tags=["Notifications"])
async def get_user_notifications(
    limit: int = Query(100, description="Limit"),
    offset: int = Query(0, description="Offset"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Get notifications for current user.
    
    Args:
        limit (int): Limit
        offset (int): Offset
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        List[NotificationResponseDTO]: List of notifications
    """
    notification_service = NotificationService(db)
    return notification_service.get_user_notifications(user_id, limit, offset)


@app.get("/notifications/unread", response_model=List[NotificationResponseDTO], tags=["Notifications"])
async def get_unread_notifications(
    limit: int = Query(100, description="Limit"),
    offset: int = Query(0, description="Offset"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Get unread notifications for current user.
    
    Args:
        limit (int): Limit
        offset (int): Offset
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        List[NotificationResponseDTO]: List of unread notifications
    """
    notification_service = NotificationService(db)
    return notification_service.get_unread_notifications(user_id, limit, offset)


@app.put("/notifications/{notification_id}/read", response_model=NotificationResponseDTO, tags=["Notifications"])
async def mark_notification_as_read(
    notification_id: str = Path(..., description="Notification ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Mark a notification as read.
    
    Args:
        notification_id (str): Notification ID
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        NotificationResponseDTO: Updated notification
    """
    notification_service = NotificationService(db)
    return notification_service.mark_notification_as_read(notification_id, user_id)


@app.put("/notifications/read-all", tags=["Notifications"])
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Mark all notifications as read for current user.
    
    Args:
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        Dict[str, Any]: Success response
    """
    notification_service = NotificationService(db)
    return notification_service.mark_all_notifications_as_read(user_id)


@app.delete("/notifications/{notification_id}", tags=["Notifications"])
async def delete_notification(
    notification_id: str = Path(..., description="Notification ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Delete a notification.
    
    Args:
        notification_id (str): Notification ID
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        Dict[str, Any]: Success response
    """
    notification_service = NotificationService(db)
    return notification_service.delete_notification(notification_id, user_id)


# Notification preferences endpoints
@app.get("/notification-preferences", response_model=NotificationPreferencesDTO, tags=["Notification Preferences"])
async def get_notification_preferences(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Get notification preferences for current user.
    
    Args:
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        NotificationPreferencesDTO: Notification preferences
    """
    notification_service = NotificationService(db)
    return notification_service.get_notification_preferences(user_id)


@app.put("/notification-preferences", response_model=NotificationPreferencesDTO, tags=["Notification Preferences"])
async def update_notification_preferences(
    preferences_data: NotificationPreferencesUpdateDTO,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Update notification preferences for current user.
    
    Args:
        preferences_data (NotificationPreferencesUpdateDTO): Preferences data
        db (Session): Database session
        user_id (str): User ID
        
    Returns:
        NotificationPreferencesDTO: Updated notification preferences
    """
    notification_service = NotificationService(db)
    return notification_service.update_notification_preferences(user_id, preferences_data)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dict[str, str]: Health status
    """
    return {"status": "healthy"}