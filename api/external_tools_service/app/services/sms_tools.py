import os
try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

def send_sms_twilio(to: str, body: str) -> bool:
    """
    Envía un SMS usando Twilio.
    """
    if not TwilioClient:
        print("Falta la librería Twilio.")
        return False
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    if not all([account_sid, auth_token, from_number]):
        print("Faltan variables de entorno para Twilio.")
        return False
    try:
        client = TwilioClient(account_sid, auth_token)
        client.messages.create(body=body, from_=from_number, to=to)
        return True
    except Exception as e:
        print(f"Twilio error: {e}")
        return False 