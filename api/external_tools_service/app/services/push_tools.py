import os
import requests

def send_gotify_notification(message: str, title: str = "Notificación", priority: int = 5) -> bool:
    """
    Envía una notificación push usando Gotify.
    """
    gotify_url = os.getenv("GOTIFY_URL")
    gotify_token = os.getenv("GOTIFY_TOKEN")
    if not gotify_url or not gotify_token:
        print("Faltan variables de entorno para Gotify.")
        return False
    payload = {"title": title, "message": message, "priority": priority}
    headers = {"X-Gotify-Key": gotify_token}
    try:
        response = requests.post(f"{gotify_url}/message", json=payload, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Gotify error: {e}")
        return False 