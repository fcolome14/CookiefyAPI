from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app.core.security import pwd_context
from app.services.auth_service import GenerateAuthCode
from app.utils.date_time import TimeUtils
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email_or_username(self, email: str, username: str) -> User | None:
        """Check if a user with the given email or username exists."""
        return (
            self.db.query(User)
            .filter(or_(User.email == email, User.username == username))
            .first()
        )

    def add_user(self, user: User) -> User:
        """Add a new user to the database."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class UserService:
    """Service for managing user creation."""

    def __init__(self, db: Session, auth_code_service: GenerateAuthCode, time_utils: TimeUtils):
        self.db = db
        self.auth_code_service = auth_code_service
        self.time_utils = time_utils
        self.user_repo = UserRepository(db)

    async def create_user(self, user_input: UserCreate) -> UserRead | None:
        """Create a new user after validating input and generating auth code."""
        if self._check_existing_account(user_input.email, user_input.username):
            logger.error("Account already exists for email '%s' or username '%s'", user_input.email, user_input.username)
            return None
        
        auth_code_result = await self.auth_code_service.generate_code(self.db)
        if auth_code_result["status"] == "error":
            logger.error("Failed to generate auth code: %s", auth_code_result["message"])
            return None

        code = int(auth_code_result["message"])
        code_expiration = self.time_utils.exp_time()

        return self._create_new_user(user_input, code, code_expiration)

    def _check_existing_account(self, email: str, username: str) -> bool:
        """Check if an account exists with the given email or username."""
        existing_user = self.user_repo.get_user_by_email_or_username(email, username)
        return existing_user is not None

    def _create_new_user(self, user_input: UserCreate, code: int, code_exp: datetime) -> UserRead | None:
        """Add a new user to the database."""
        hashed_password = pwd_context.hash(user_input.password)

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
            return user
        except IntegrityError:
            self.db.rollback()
            logger.error("Failed to create user: Email or username already exists")
            return None
        except Exception as exc:
            self.db.rollback()
            logger.error("Unexpected error during user creation: %s", exc)
            return None