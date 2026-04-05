"""Email sending service using SMTP configuration from settings."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
import os

from src.core.config import settings
from src.database.connection import init_db
from sqlalchemy.orm import Session
from src.database.crud import get_user_settings


def send_email(
    *,
    from_email: str,
    to_emails: List[str],
    subject: str,
    body: str,
    cc_emails: Optional[List[str]] = None,
    bcc_emails: Optional[List[str]] = None,
    attachment_paths: Optional[List[str]] = None,
    use_html: bool = True,
) -> tuple:
    """
    Send an email via SMTP.

    Returns:
        tuple: (success: bool, message: str)
    """
    engine = init_db()
    with Session(engine) as db:
        db_settings = get_user_settings(db)
        smtp_host = db_settings.smtp_host or settings.smtp_host
        smtp_username = db_settings.smtp_username or settings.smtp_username
        smtp_password = db_settings.smtp_password or settings.smtp_password
        smtp_port = db_settings.smtp_port or settings.smtp_port

    if not smtp_host or not smtp_username or not smtp_password:
        return False, "SMTP not configured. Configure in Settings UI or .env"

    cc_emails = cc_emails or []
    bcc_emails = bcc_emails or []
    attachment_paths = attachment_paths or []

    try:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject

        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)

        # Support plain text: convert newlines to <br> for HTML
        if use_html and "<" not in body:
            body = body.replace("\n", "<br>\n")
        msg.attach(MIMEText(body, "html" if use_html else "plain"))

        for file_path in attachment_paths:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {os.path.basename(file_path)}",
                    )
                    msg.attach(part)

        all_recipients = to_emails + cc_emails + bcc_emails

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, all_recipients, msg.as_string())

        return True, f"Email sent successfully to {', '.join(to_emails)}"

    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP authentication failed. Check username/app password: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
