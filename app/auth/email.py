from app.core_config import settings


def send_verification_email(email: str, verify_url: str) -> None:
    # For now (fast demo + no external setup): log the link.
    # If you want “real email” later, we can plug SendGrid/SMTP here.
    print(f"[EMAIL VERIFY] To: {email}")
    print(f"[EMAIL VERIFY] Link: {verify_url}")
    print(f"[EMAIL VERIFY] (APP_BASE_URL={settings.APP_BASE_URL})")
