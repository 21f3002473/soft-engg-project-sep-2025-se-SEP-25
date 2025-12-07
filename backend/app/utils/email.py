import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.config import Config

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service using MailHog for development/testing.

    MailHog captures all emails sent via SMTP and displays them in a web UI.
    Perfect for development and testing without sending real emails.
    """

    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_password = Config.SMTP_PASSWORD
        self.from_email = Config.SMTP_FROM_EMAIL
        self.from_name = Config.SMTP_FROM_NAME

    def send_email(
        self,
        to_email: str | List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Send email via MailHog SMTP server.

        Args:
            to_email: Recipient email(s)
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            cc: Optional CC recipients
            bcc: Optional BCC recipients

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"

            if isinstance(to_email, str):
                to_email = [to_email]
            msg["To"] = ", ".join(to_email)

            if cc:
                msg["Cc"] = ", ".join(cc)

            text_part = MIMEText(body, "plain", "utf-8")
            msg.attach(text_part)

            if html_body:
                html_part = MIMEText(html_body, "html", "utf-8")
                msg.attach(html_part)

            all_recipients = to_email + (cc or []) + (bcc or [])

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(msg, self.from_email, all_recipients)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return False


def get_email_service() -> EmailService:
    """Get email service instance."""
    return EmailService()
