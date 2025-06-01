from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from api.shared.models.notification import Notification, NotificationPreference
from api.shared.utils.rabbitmq import RabbitMQManager
from schemas.notification import (
    NotificationCreateDTO,
    NotificationResponseDTO,
    NotificationUpdateDTO,
    NotificationBatchCreateDTO,
    NotificationPreferencesDTO,
    NotificationPreferencesUpdateDTO,
    NotificationChannel
)
from observers.notification_observer import (
    NotificationObserver,
    EmailNotificationObserver,
    PushNotificationObserver,
    SMSNotificationObserver
)


class NotificationService:
    """Service for notification operations"""
    
    def __init__(self, db: Session):
        """
        Initialize NotificationService.
        
        Args:
            db (Session): Database session
        """
        self.db = db
        self.rabbitmq_manager = RabbitMQManager()
        
        # Initialize observers
        self.observers: List[NotificationObserver] = [
            EmailNotificationObserver(),
            PushNotificationObserver(),
            SMSNotificationObserver()
        ]
    
    def create_notification(self, notification_data: NotificationCreateDTO) -> NotificationResponseDTO:
        """
        Create a new notification.
        
        Args:
            notification_data (NotificationCreateDTO): Notification data
            
        Returns:
            NotificationResponseDTO: Created notification
        """
        # Check user notification preferences
        preferences = self._get_or_create_preferences(notification_data.user_id)
        
        # Filter channels based on user preferences
        channels = []
        for channel in notification_data.channels:
            if channel == NotificationChannel.EMAIL and preferences.email_enabled:
                channels.append(channel)
            elif channel == NotificationChannel.PUSH and preferences.push_enabled:
                channels.append(channel)
            elif channel == NotificationChannel.SMS and preferences.sms_enabled:
                channels.append(channel)
            elif channel == NotificationChannel.IN_APP and preferences.in_app_enabled:
                channels.append(channel)
        
        # Check if notification should be sent based on type preferences
        if preferences.preferences_by_type:
            type_preferences = preferences.preferences_by_type.get(notification_data.type, {})
            filtered_channels = []
            for channel in channels:
                if type_preferences.get(channel, True):
                    filtered_channels.append(channel)
            channels = filtered_channels
        
        # Check if notification should be sent during quiet hours
        if preferences.quiet_hours_enabled and channels:
            current_time = datetime.utcnow().strftime("%H:%M")
            if preferences.quiet_hours_start and preferences.quiet_hours_end:
                if preferences.quiet_hours_start <= current_time <= preferences.quiet_hours_end:
                    # Only allow in-app notifications during quiet hours
                    channels = [channel for channel in channels if channel == NotificationChannel.IN_APP]
        
        # Create notification
        notification = Notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            priority=notification_data.priority,
            channels=channels,
            related_entity_type=notification_data.related_entity_type,
            related_entity_id=notification_data.related_entity_id,
            action_url=notification_data.action_url,
            metadata=notification_data.metadata,
            scheduled_at=notification_data.scheduled_at
        )
        
        # Add notification to database
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Send notification to observers if not scheduled
        if not notification_data.scheduled_at:
            self._send_notification(notification)
        
        # Return notification
        return self._notification_to_dto(notification)
    
    def create_batch_notifications(self, notification_data: NotificationBatchCreateDTO) -> List[NotificationResponseDTO]:
        """
        Create multiple notifications at once.
        
        Args:
            notification_data (NotificationBatchCreateDTO): Notification data
            
        Returns:
            List[NotificationResponseDTO]: List of created notifications
        """
        notifications = []
        
        for user_id in notification_data.user_ids:
            # Create notification data for user
            user_notification_data = NotificationCreateDTO(
                user_id=user_id,
                type=notification_data.type,
                title=notification_data.title,
                message=notification_data.message,
                priority=notification_data.priority,
                channels=notification_data.channels,
                related_entity_type=notification_data.related_entity_type,
                related_entity_id=notification_data.related_entity_id,
                action_url=notification_data.action_url,
                metadata=notification_data.metadata,
                scheduled_at=notification_data.scheduled_at
            )
            
            # Create notification
            notification = self.create_notification(user_notification_data)
            notifications.append(notification)
        
        return notifications
    
    def get_user_notifications(self, user_id: str, limit: int = 100, offset: int = 0) -> List[NotificationResponseDTO]:
        """
        Get notifications for a user.
        
        Args:
            user_id (str): User ID
            limit (int, optional): Limit. Defaults to 100.
            offset (int, optional): Offset. Defaults to 0.
            
        Returns:
            List[NotificationResponseDTO]: List of notifications
        """
        # Get notifications
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Return notifications
        return [self._notification_to_dto(notification) for notification in notifications]
    
    def get_unread_notifications(self, user_id: str, limit: int = 100, offset: int = 0) -> List[NotificationResponseDTO]:
        """
        Get unread notifications for a user.
        
        Args:
            user_id (str): User ID
            limit (int, optional): Limit. Defaults to 100.
            offset (int, optional): Offset. Defaults to 0.
            
        Returns:
            List[NotificationResponseDTO]: List of unread notifications
        """
        # Get notifications
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Return notifications
        return [self._notification_to_dto(notification) for notification in notifications]
    
    def mark_notification_as_read(self, notification_id: str, user_id: str) -> NotificationResponseDTO:
        """
        Mark a notification as read.
        
        Args:
            notification_id (str): Notification ID
            user_id (str): User ID
            
        Returns:
            NotificationResponseDTO: Updated notification
            
        Raises:
            Exception: If notification not found or user does not have permission
        """
        # Get notification
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        # Check if notification exists
        if not notification:
            raise Exception("Notification not found or user does not have permission")
        
        # Update notification
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        # Update notification in database
        self.db.commit()
        self.db.refresh(notification)
        
        # Return notification
        return self._notification_to_dto(notification)
    
    def mark_all_notifications_as_read(self, user_id: str) -> Dict[str, Any]:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            Dict[str, Any]: Success response
        """
        # Update notifications
        self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        # Commit changes
        self.db.commit()
        
        # Return success response
        return {"message": "All notifications marked as read"}
    
    def delete_notification(self, notification_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a notification.
        
        Args:
            notification_id (str): Notification ID
            user_id (str): User ID
            
        Returns:
            Dict[str, Any]: Success response
            
        Raises:
            Exception: If notification not found or user does not have permission
        """
        # Get notification
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        # Check if notification exists
        if not notification:
            raise Exception("Notification not found or user does not have permission")
        
        # Delete notification
        self.db.delete(notification)
        self.db.commit()
        
        # Return success response
        return {"message": "Notification deleted successfully"}
    
    def get_notification_preferences(self, user_id: str) -> NotificationPreferencesDTO:
        """
        Get notification preferences for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            NotificationPreferencesDTO: Notification preferences
        """
        # Get or create preferences
        preferences = self._get_or_create_preferences(user_id)
        
        # Return preferences
        return NotificationPreferencesDTO(
            user_id=preferences.user_id,
            email_enabled=preferences.email_enabled,
            push_enabled=preferences.push_enabled,
            sms_enabled=preferences.sms_enabled,
            in_app_enabled=preferences.in_app_enabled,
            digest_enabled=preferences.digest_enabled,
            digest_frequency=preferences.digest_frequency,
            quiet_hours_enabled=preferences.quiet_hours_enabled,
            quiet_hours_start=preferences.quiet_hours_start,
            quiet_hours_end=preferences.quiet_hours_end,
            preferences_by_type=preferences.preferences_by_type
        )
    
    def update_notification_preferences(self, user_id: str, preferences_data: NotificationPreferencesUpdateDTO) -> NotificationPreferencesDTO:
        """
        Update notification preferences for a user.
        
        Args:
            user_id (str): User ID
            preferences_data (NotificationPreferencesUpdateDTO): Preferences data
            
        Returns:
            NotificationPreferencesDTO: Updated notification preferences
        """
        # Get or create preferences
        preferences = self._get_or_create_preferences(user_id)
        
        # Update preferences
        if preferences_data.email_enabled is not None:
            preferences.email_enabled = preferences_data.email_enabled
        
        if preferences_data.push_enabled is not None:
            preferences.push_enabled = preferences_data.push_enabled
        
        if preferences_data.sms_enabled is not None:
            preferences.sms_enabled = preferences_data.sms_enabled
        
        if preferences_data.in_app_enabled is not None:
            preferences.in_app_enabled = preferences_data.in_app_enabled
        
        if preferences_data.digest_enabled is not None:
            preferences.digest_enabled = preferences_data.digest_enabled
        
        if preferences_data.digest_frequency is not None:
            preferences.digest_frequency = preferences_data.digest_frequency
        
        if preferences_data.quiet_hours_enabled is not None:
            preferences.quiet_hours_enabled = preferences_data.quiet_hours_enabled
        
        if preferences_data.quiet_hours_start is not None:
            preferences.quiet_hours_start = preferences_data.quiet_hours_start
        
        if preferences_data.quiet_hours_end is not None:
            preferences.quiet_hours_end = preferences_data.quiet_hours_end
        
        if preferences_data.preferences_by_type is not None:
            preferences.preferences_by_type = preferences_data.preferences_by_type
        
        # Update preferences in database
        self.db.commit()
        self.db.refresh(preferences)
        
        # Return preferences
        return NotificationPreferencesDTO(
            user_id=preferences.user_id,
            email_enabled=preferences.email_enabled,
            push_enabled=preferences.push_enabled,
            sms_enabled=preferences.sms_enabled,
            in_app_enabled=preferences.in_app_enabled,
            digest_enabled=preferences.digest_enabled,
            digest_frequency=preferences.digest_frequency,
            quiet_hours_enabled=preferences.quiet_hours_enabled,
            quiet_hours_start=preferences.quiet_hours_start,
            quiet_hours_end=preferences.quiet_hours_end,
            preferences_by_type=preferences.preferences_by_type
        )
    
    def _get_or_create_preferences(self, user_id: str) -> NotificationPreference:
        """
        Get or create notification preferences for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            NotificationPreference: Notification preferences
        """
        # Get preferences
        preferences = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        # Create preferences if not exists
        if not preferences:
            preferences = NotificationPreference(
                user_id=user_id,
                email_enabled=True,
                push_enabled=True,
                sms_enabled=False,
                in_app_enabled=True,
                digest_enabled=False,
                quiet_hours_enabled=False
            )
            
            # Add preferences to database
            self.db.add(preferences)
            self.db.commit()
            self.db.refresh(preferences)
        
        return preferences
    
    def _send_notification(self, notification: Notification) -> None:
        """
        Send notification to observers.
        
        Args:
            notification (Notification): Notification to send
        """
        # Update sent_at
        notification.sent_at = datetime.utcnow()
        self.db.commit()
        
        # Notify observers
        for observer in self.observers:
            observer.notify(notification)
        
        # Publish notification to RabbitMQ
        try:
            # Ensure connection
            self.rabbitmq_manager.ensure_connection()
            
            # Declare exchange
            self.rabbitmq_manager.declare_exchange("notifications", "topic")
            
            # Publish notification
            self.rabbitmq_manager.publish(
                exchange_name="notifications",
                routing_key=f"notification.{notification.type}",
                message=self._notification_to_dict(notification)
            )
        except Exception as e:
            # Log error
            print(f"Error publishing notification to RabbitMQ: {e}")
    
    def _notification_to_dto(self, notification: Notification) -> NotificationResponseDTO:
        """
        Convert Notification model to NotificationResponseDTO.
        
        Args:
            notification (Notification): Notification model
            
        Returns:
            NotificationResponseDTO: Notification DTO
        """
        return NotificationResponseDTO(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            priority=notification.priority,
            channels=notification.channels,
            related_entity_type=notification.related_entity_type,
            related_entity_id=notification.related_entity_id,
            action_url=notification.action_url,
            metadata=notification.metadata,
            is_read=notification.is_read,
            read_at=notification.read_at,
            created_at=notification.created_at,
            scheduled_at=notification.scheduled_at,
            sent_at=notification.sent_at
        )
    
    def _notification_to_dict(self, notification: Notification) -> Dict[str, Any]:
        """
        Convert Notification model to dictionary.
        
        Args:
            notification (Notification): Notification model
            
        Returns:
            Dict[str, Any]: Notification dictionary
        """
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "priority": notification.priority,
            "channels": notification.channels,
            "related_entity_type": notification.related_entity_type,
            "related_entity_id": notification.related_entity_id,
            "action_url": notification.action_url,
            "metadata": notification.metadata,
            "is_read": notification.is_read,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "created_at": notification.created_at.isoformat(),
            "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None
        }