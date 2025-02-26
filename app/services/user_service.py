from sqlalchemy.orm import Session
import aiofiles
from pathlib import Path
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from sqlalchemy.exc import IntegrityError
from string import Template
from app.services.auth_service import AuthCodeManager
from app.utils.date_time import TimeUtils
from app.utils.email import EmailService, EmailSenderFactory
from datetime import datetime
from app.core.config import settings
from app.core.security import create_access_token
import logging
from app.repositories.user_repo import UserRepository
from app.core.security import hash_password
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)
CODE_VALIDATION_ENDPOINT = "/auth/token"

class EmailTemplates(Enum):
    NEW_USER = "email_code.html"
    PASSWORD_RECOVERY = "email_pwd_recovery.html"

class IUserService:
    """Interface service for managing users."""

    @abstractmethod
    def create_user(self, user_input: UserCreate) -> UserRead | None:
        pass
    
    @abstractmethod
    def auth_user(self, user_email: str) -> UserRead | None:
        pass
    
    @abstractmethod
    def change_password(self, user_email: str, user_new_password: str) -> UserRead | None:
        pass

class UserService(IUserService):
    """Service for managing user creation."""

    def __init__(self, db: Session, auth_code_service: AuthCodeManager, time_utils: TimeUtils):
        self.db = db
        self.auth_code_service = auth_code_service
        self.time_utils = time_utils
        self.user_repo = UserRepository(db)

    async def create_user(self, user_input: UserCreate) -> UserRead | None:
        """Create a new user after validating input and generating auth code."""
        if self._check_existing_account(user_input.email, user_input.username):
            msg = f"Account already exists for email {user_input.email} or username {user_input.username}"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        auth_code_result = await self.auth_code_service.generate_unique_code()
        if auth_code_result["status"] == "error":
            msg = f"Failed to generate auth code: {auth_code_result['message']}"
            logger.error(msg)
            return {"status": "error", "message": msg}

        code = int(auth_code_result["message"])
        code_expiration = self.time_utils.exp_time(settings.email_auth_code_expire_minutes)
        tmp = EmailTemplates.NEW_USER.value
        
        sent_email = await self._send_auth_email(code, user_input.email, tmp, "Your Verification Code")
        if sent_email["status"] == "error":
            msg = "Failed to send email"
            logger.error(msg)
            return {"status": "error", "message": msg}

        return self._create_new_user(user_input, code, code_expiration)
    
    async def auth_user(self, user_email: str) -> UserRead | None:
        """Authenticate user by generating auth code."""
        user: User = self._check_existing_account(user_email, None)
        if not user.is_active:
            return {"status": "error", "message": "User account is not activated"}
        
        auth_code_result = await self.auth_code_service.generate_unique_code()
        if auth_code_result["status"] == "error":
            msg = f"Failed to generate auth code: {auth_code_result['message']}"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        code = int(auth_code_result["message"])
        code_expiration = self.time_utils.exp_time(settings.email_recovery_code_expire_minutes)
        
        user.code = code
        user.code_exp = code_expiration
        tmp = EmailTemplates.PASSWORD_RECOVERY.value
        
        sent_email = await self._send_auth_email(code, user_email, tmp, "Your Recovery Code")
        if sent_email["status"] == "error":
            msg = "Failed to send email"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        user = self.user_repo.update_user(user)
        return {"status": "success", "message": user}

    def _check_existing_account(self, email: str, username: str) -> bool:
        """Check if an account exists with the given email or username."""
        existing_user = self.user_repo.get_user_by_email_or_username(email, username)
        if existing_user:
            return existing_user
        return None
    
    async def _send_auth_email(self, code: int, recipient: str, template_name: str, title: str) -> dict:
        """Send an authentication email with a verification code."""
        email_sender = EmailSenderFactory.get_email_sender()
        email_service = EmailService(email_sender)

        template_content = await self._get_email_template(template_name)
        if not template_content:
            logger.error("Email template not found")
            return {"status": "error", "message": "Email template not found"}
        
        data={"user": recipient, "code": code}
        jwt = create_access_token(data)

        html_content = self._build_email_content(template_content, template_name, code, jwt)
        if not html_content:
            logger.error("Failed to build email content")
            return {"status": "error", "message": "Failed to build email content"}

        subject = title
        try:
            if await email_service.send_email(to=recipient, subject=subject, body=html_content):
                logger.info("Email sent successfully to %s", recipient)
                return {"status": "success", "message": "Email sent successfully!"}
            else:
                logger.error("Failed to send email")
                return {"status": "error", "message": "Failed to send email"}
        except Exception as e:
            logger.exception("Exception occurred while sending email: %s", e)
            return {"status": "error", "message": f"Unexpected error: {e}"}

    async def _get_email_template(self, template_name: str) -> str | None:
        """Read the email template file asynchronously."""
        template_path = Path("app/tmp") / template_name

        if not template_path.exists():
            logger.error("Email template not found at %s", template_path)
            return {"status": "error", "message": "Email template not found"}

        try:
            async with aiofiles.open(template_path, mode="r") as f:
                return await f.read()
        except Exception as e:
            logger.exception("Failed to read email template: %s", e)
            return {"status": "error", "message": "Failed to read email template"}

    def _build_email_content(self, template_content: str, template_name: str, code: int, jwt: str) -> str | None:
        """Substitute placeholders in the email template."""
        try:
            endpoint_url = f"{settings.domain}{CODE_VALIDATION_ENDPOINT}"
            template = Template(template_content)
            if template_name == EmailTemplates.NEW_USER.value:
                return template.substitute(
                    code_exp=settings.email_auth_code_expire_minutes,
                    verification_token=jwt,
                    verification_url=endpoint_url,
                    verification_code=str(code),
                )
            return template.substitute(
                    recovery_code_exp=settings.email_recovery_code_expire_minutes,
                    recovery_code=code,
                    verification_token=jwt,
                    verification_url=endpoint_url,
                    verification_code=str(code),
                )
        except KeyError as e:
            logger.error("Missing placeholder in template: %s", e)
            return {"status": "error", "message": "Missing placeholder in template"}
        except Exception as e:
            logger.exception("Failed to build email content: %s", e)
            return {"status": "error", "message": "Failed to build email content"}

    def _create_new_user(self, user_input: UserCreate, code: int, code_exp: datetime) -> UserRead | None:
        """Add a new user to the database."""
        #hashed_password = pwd_context.hash(user_input.password)
        hashed_password = hash_password(user_input.password)

        new_user = User(
            name=user_input.full_name,
            username=user_input.username.lower(),
            email=user_input.email.lower(),
            is_active=False,
            code=code,
            code_exp=code_exp,
            hashed_password=hashed_password,
        )

        try:
            user = self.user_repo.add_user(new_user)
            logger.info("User created successfully with ID %d", user.id)
            return {"status": "success", "message": user}
        except IntegrityError:
            self.db.rollback()
            logger.error("Failed to create user: Email or username already exists")
            return {"status": "error", "message": "Failed to create user: Email or username already exists"}
        except Exception as exc:
            self.db.rollback()
            logger.error("Unexpected error during user creation: %s", exc)
            return {"status": "error", "message": "Unexpected error during user creation"}

class NewUserPassword(IUserService):
    """Manage user new password."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def create_user(self, user_input: UserCreate) -> UserRead | None:
        raise NotImplementedError("This method is not implemented for NewUserPassword.")
    
    def auth_user(self, user_email: str) -> UserRead | None:
        raise NotImplementedError("This method is not implemented for NewUserPassword.")
    
    def change_password(self, user_email: str, user_new_password: str) -> UserRead | None:
        user: User = self.user_repo.get_user_by_email_or_username(user_email, None)
        hashed_password = hash_password(user_new_password)
        user.hashed_password = hashed_password
        result = self.user_repo.update_user(user)
        if result:
            logger.info("User password changed")
            return {"status": "success", "message": user} 
        return {"status": "error", "message": "Error while updating in database"} 