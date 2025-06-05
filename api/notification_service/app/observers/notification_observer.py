import os
from abc import ABC, abstractmethod

from api.notification_service.app.schemas.notification import NotificationChannel
from api.shared.models.notification import Notification
from api.external_tools_service.app.services.email_tools import send_email_brevo
from api.external_tools_service.app.services.push_tools import send_gotify_notification
from api.external_tools_service.app.services.sms_tools import send_sms_twilio


class NotificationObserver(ABC):
    """Abstract observer for notifications"""

    @abstractmethod
    def notify(self, notification: Notification) -> None:
        """
        Notify observer about a notification.

        Args:
            notification (Notification): Notification to send
        """


class EmailNotificationObserver(NotificationObserver):
    """Observer for email notifications"""
    
    def notify(self, notification: Notification) -> None:
        """
        Send notification via email (Brevo).

        Args:
            notification (Notification): Notification to send
        """
        if NotificationChannel.EMAIL not in notification.channels:
            return
        try:
            to = self._get_user_email(notification.user_id)
            subject = notification.title
            body = self._create_email_body(notification)
            send_email_brevo(to, subject, body)
        except Exception as e:
            print(f"Error sending email notification: {e}")

    def _get_user_email(self, user_id: str) -> str:
        """
        Get user email.

        Args:
            user_id (str): User ID

        Returns:
            str: User email
        """
        # In a real application, you would get the user email from the database
        # This is a placeholder implementation
        return f"{user_id}@example.com"

    def _create_email_body(self, notification: Notification) -> str:
        """
        Create email body.

        Args:
            notification (Notification): Notification

        Returns:
            str: Email body
        """
        # Create email body
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 10px; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 10px; font-size: 12px; }}
                .button {{ display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{notification.title}</h2>
                </div>
                <div class="content">
                    <p>{notification.message}</p>
                    {f'<a href="{notification.action_url}" class="button">View Details</a>' if notification.action_url else ''}
                </div>
                <div class="footer">
                    <p>This is an automated message from TaskHub. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return body



class PushNotificationObserver(NotificationObserver):
    """Observer for push notifications"""
    
    def notify(self, notification: Notification) -> None:
        """
        Send notification via push.

        Args:
            notification (Notification): Notification to send
        """
        if NotificationChannel.PUSH not in notification.channels:
            return
        try:
            message = notification.message
            title = notification.title
            send_gotify_notification(message, title)
        except Exception as e:
            print(f"Error sending push notification: {e}")



class SMSNotificationObserver(NotificationObserver):
    """Observer for SMS notifications"""
    
    def notify(self, notification: Notification) -> None:
        """
        Send notification via SMS.

        Args:
            notification (Notification): Notification to send
        """
        if NotificationChannel.SMS not in notification.channels:
            return
        try:
            phone_number = self._get_user_phone_number(notification.user_id)
            send_sms_twilio(phone_number, notification.message)
        except Exception as e:
            print(f"Error sending SMS notification: {e}")

    def _get_user_phone_number(self, user_id: str) -> str:
        """
        Get user phone number.

        Args:
            user_id (str): User ID

        Returns:
            str: User phone number
        """
        # In a real application, you would get the user phone number from the database
        # This is a placeholder implementation
        return f"+1234567890"
