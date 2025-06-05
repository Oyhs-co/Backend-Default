import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def send_email_brevo(to: str, subject: str, body: str) -> bool:
    """
    Envía un email usando la API de Brevo (Sendinblue).
    """
    api_key = os.getenv("BREVO_API_KEY")
    from_addr = os.getenv("BREVO_FROM", "noreply@example.com")
    if not api_key:
        print("Falta la variable BREVO_API_KEY")
        return False
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to}],
        sender={"email": from_addr},
        subject=subject,
        html_content=body
    )
    try:
        api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Brevo error: {e}")
        return False 