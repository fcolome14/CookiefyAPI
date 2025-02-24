from abc import ABC, abstractmethod
from email.message import EmailMessage
import smtplib
import ssl
from typing import List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Dependency inversion
class EmailSender(ABC):
    @abstractmethod
    def send_email(self, email_message: EmailMessage) -> bool:
        """Send an email using the implemented method."""
        pass


# Strategy pattern
class SMTPEmailSender(EmailSender):
    """Concrete implementation for sending emails via SMTP."""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, email_message: EmailMessage) -> bool:
        """Send email using SMTP protocol."""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(email_message)
            logger.info("Email sent successfully to %s", email_message["To"])
            return True
        except Exception as e:
            logger.error("Failed to send email: %s", e)
            return False


# Builder pattern
class EmailBuilder:
    """Builder for creating email messages."""

    def __init__(self):
        self._email = EmailMessage()

    def set_sender(self, sender: str) -> "EmailBuilder":
        self._email["From"] = sender
        return self

    def set_recipient(self, recipient: str) -> "EmailBuilder":
        self._email["To"] = recipient
        return self

    def set_subject(self, subject: str) -> "EmailBuilder":
        self._email["Subject"] = subject
        return self

    def set_body(self, body: str, content_type: str = "html") -> "EmailBuilder":
        self._email.set_content(body, subtype=content_type)
        return self

    def build(self) -> EmailMessage:
        """Return the constructed EmailMessage."""
        return self._email


# Facade pattern
class EmailService:
    """Service to send emails using a given sender strategy."""

    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email with the provided details."""
        email_message = (
            EmailBuilder()
            .set_sender(settings.email)
            .set_recipient(to)
            .set_subject(subject)
            .set_body(body)
            .build()
        )

        return self.email_sender.send_email(email_message)


# Factory pattern
class EmailSenderFactory:
    """Factory to create email sender instances."""

    @staticmethod
    def get_email_sender() -> EmailSender:
        """Return an appropriate email sender based on settings."""
        return SMTPEmailSender(
            smtp_server=settings.smtp_server,
            smtp_port=settings.smtp_port,
            username=settings.email,
            password=settings.email_password,
        )