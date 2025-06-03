import os
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv

from api.notification_service.app.schemas.notification import NotificationChannel
from api.shared.models.notification import Notification

# Load environment variables
load_dotenv()

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@taskhub.com")

# Push notification configuration
PUSH_API_KEY = os.getenv("PUSH_API_KEY", "")
PUSH_API_URL = os.getenv("PUSH_API_URL", "")

# SMS configuration
SMS_API_KEY = os.getenv("SMS_API_KEY", "")
SMS_API_URL = os.getenv("SMS_API_URL", "")


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
        Send notification via email.

        Args:
            notification (Notification): Notification to send
        """
        # Check if email channel is enabled
        if NotificationChannel.EMAIL not in (notification.channels or {}):
            return

        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = EMAIL_FROM
            message["To"] = self._get_user_email(notification.user_id)
            message["Subject"] = notification.title

            # Add message body
            body = self._create_email_body(notification)
            message.attach(MIMEText(body, "html"))

            # Send email
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(message)
        except Exception as e:
            # Log error
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
        # Check if push channel is enabled
        if NotificationChannel.PUSH not in (notification.channels or {}):
            return

        try:
            # Get user device tokens
            device_tokens = self._get_user_device_tokens(notification.user_id)

            # Send push notification to each device
            for token in device_tokens:
                self._send_push_notification(token, notification)
        except Exception as e:
            # Log error
            print(f"Error sending push notification: {e}")

    def _get_user_device_tokens(self, user_id: str) -> list:
        """
        Get user device tokens.

        Args:
            user_id (str): User ID

        Returns:
            list: List of device tokens
        """
        # In a real application, you would get the user device tokens from the database
        # This is a placeholder implementation
        return [f"device_token_{user_id}"]

    def _send_push_notification(self, token: str, notification: Notification) -> None:
        """
        Send push notification to a device.

        Args:
            token (str): Device token
            notification (Notification): Notification
        """
        # Create payload
        payload = {
            "to": token,
            "notification": {
                "title": notification.title,
                "body": notification.message,
                "click_action": notification.action_url,
            },
            "data": {
                "notification_id": notification.id,
                "type": notification.type,
                "related_entity_type": notification.related_entity_type,
                "related_entity_id": notification.related_entity_id,
            },
        }

        # Send push notification
        if PUSH_API_URL and PUSH_API_KEY:
            headers = {
                "Authorization": f"key={PUSH_API_KEY}",
                "Content-Type": "application/json",
            }

            response = requests.post(PUSH_API_URL, json=payload, headers=headers)

            # Check response
            if response.status_code != 200:
                print(f"Error sending push notification: {response.text}")


class SMSNotificationObserver(NotificationObserver):
    """Observer for SMS notifications"""

    def notify(self, notification: Notification) -> None:
        """
        Send notification via SMS.

        Args:
            notification (Notification): Notification to send
        """
        # Check if SMS channel is enabled
        if NotificationChannel.SMS not in (notification.channels or {}):
            return

        try:
            # Get user phone number
            phone_number = self._get_user_phone_number(notification.user_id)

            # Send SMS
            self._send_sms(phone_number, notification)
        except Exception as e:
            # Log error
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

    def _send_sms(self, phone_number: str, notification: Notification) -> None:
        """
        Send SMS.

        Args:
            phone_number (str): Phone number
            notification (Notification): Notification
        """
        # Create message
        message = f"{notification.title}: {notification.message}"

        # Send SMS
        if SMS_API_URL and SMS_API_KEY:
            payload = {"to": phone_number, "message": message, "api_key": SMS_API_KEY}

            response = requests.post(SMS_API_URL, json=payload)

            # Check response
            if response.status_code != 200:
                print(f"Error sending SMS: {response.text}")
