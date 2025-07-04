import secrets
from string import digits
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import exists
from app.models.user import User
from app.core.security import decode_access_token, verify_password, create_access_token
from app.repositories.user_repo import UserRepository
from app.utils.date_time import TimeUtils
import logging

logger = logging.getLogger(__name__)

class AuthCredentials(ABC):
    """Abstract strategy for authentication user credentials."""

    @abstractmethod
    def validate_credentials(self, email: str, username: str, password: str) -> str:
        """Generate an authentication code."""
        pass
class AuthCodeStrategy(ABC):
    """Abstract strategy for authentication code generation and decoding."""

    @abstractmethod
    def generate_code(self) -> str:
        """Generate a random numeric authentication code."""
        pass
    
    @abstractmethod
    def validate_recovery_code(self, email: str, code: int) -> str:
        """Validate a recovery password generated code."""
        pass

class RecoveryAuthCode(AuthCodeStrategy):
    """Validate a recovery password generated code."""
    
    def __init__(self, user_repo: UserRepository, time_utils: TimeUtils):
        self.user_repo = user_repo
        self.time_utils = time_utils
    
    def generate_code(self) -> str:
        """Generate a random numeric authentication code."""
        pass
    
    def validate_recovery_code(self, email: str, code: int) -> str:
        """Validate a recovery password generated code."""
        user: User = self.user_repo.get_user_by_email_or_username(email, None)
        if not user.is_active:
            return {"status": "error", "message": "Unverified account"}
        if user.code == code:
            result = self.time_utils.is_times_exp(user.code_exp)["status"]
            if result == 'success':
                user.code = None
                user.code_exp = None
                _ = self.user_repo.update_user(user)
                return True
            return False
        return False

class TokenValidationStrategy(ABC):
    """Abstract strategy for validating JWT tokens."""

    @abstractmethod
    def validate_tenant(self, payload: dict) -> bool:
        """Check if the JWT token is associated with the expected tenant."""
        pass
    
    @abstractmethod
    def invalidate_code(self, payload: dict) -> bool:
        """Invalidate auth code."""
        pass

class AuthUserCredentials(AuthCredentials):
    """Auth user credentials when sign in"""
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    def validate_credentials(self, email: str, username: str, password: str) -> str:
        """Validate user credentials (password)."""
        user: User = self.user_repo.get_user_by_email_or_username(email, username)
        if not user:
            return {"status": "error", "message": "Account not found"}
        if not user.is_active:
            return {"status": "error", "message": "Unverified account"}
        if verify_password(password, user.hashed_password):
            return {"status": "success", "message": {"token": self.generate_jwt(user.id), "user": user}}
        return {"status": "error", "message": "Unauthorized"}
    
    def generate_jwt(self, id: int) -> str:
        data = {"id": id}
        return create_access_token(data)
    
class NumericAuthCode(AuthCodeStrategy):
    """Generate a numeric authentication code."""

    def __init__(self, length: int = 6):
        self.length = length

    def generate_code(self) -> str:
        """Generate a random numeric authentication code."""
        return "".join(secrets.choice(digits) for _ in range(self.length))

    def validate_recovery_code(self) -> str:
        """Placeholder implementation for abstract method."""
        raise NotImplementedError("This method is not implemented for NumericAuthCode.")

    def validate_code(self, code: str, db: Session) -> bool:
        """Check if the code already exists in the database."""
        return db.query(exists().where(User.code == code)).scalar()

class JWTTokenValidator(TokenValidationStrategy):
    """JWT token validation strategy."""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def validate_tenant(self, payload: dict) -> bool:
        """Check if the token belongs to the expected tenant."""
        tenant = payload.get("user")
        code = payload.get("code")
        expected_tenant: User = self.user_repo.get_user_by_email_or_username(email=tenant, username=None)
        result_tenant = tenant == expected_tenant.email
        result_code = code == expected_tenant.code
        if result_tenant and result_code:
            self.invalidate_code(expected_tenant)
            return True
        return False
    
    def invalidate_code(self, user: User):
        user.code = None
        user.code_exp = None
        user.is_active = True
        _ = self.user_repo.update_user(user)
            
class AuthCodeManager:
    """Manage the generation and validation of authentication codes."""

    def __init__(self, strategy: AuthCodeStrategy, db: Session, max_attempts: int = 10):
        self.strategy = strategy
        self.db = db
        self.max_attempts = max_attempts

    async def generate_unique_code(self) -> dict:
        """Generate a unique authentication code, ensuring it's not duplicated."""
        for _ in range(self.max_attempts):
            code = self.strategy.generate_code()
            if not self.strategy.validate_code(code, self.db):
                return {"status": "success", "message": code}

        return {"status": "error", "message": "Failed to generate a unique code after multiple attempts."}

class AuthCodeDecoder:
    """Decode and validate JWT payload for auth codes."""

    def __init__(self, validator: TokenValidationStrategy, db: Session):
        self.validator = validator
        self.db = db

    def decode_and_validate(self, jwt_token: str) -> dict:
        """Decode JWT and validate expiration and tenant."""
        payload = decode_access_token(jwt_token)
        if not payload:
            return {"status": "error", "message": "Invalid code"}

        if not self.validator.validate_tenant(payload):
            return {"status": "error", "message": "Unauthorized"}

        return {"status": "success", "message": "We are ready!"}
