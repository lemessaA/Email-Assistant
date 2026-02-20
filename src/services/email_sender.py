"""Email sending service using SMTP configuration from settings."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
import os

from src.core.config import settings


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
    if not settings.smtp_host or not settings.smtp_username or not settings.smtp_password:
        return False, "SMTP not configured. Set SMTP_HOST, SMTP_USERNAME, and SMTP_PASSWORD in .env"

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

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(from_email, all_recipients, msg.as_string())

        return True, f"Email sent successfully to {', '.join(to_emails)}"

    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP authentication failed. Check username/app password: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
