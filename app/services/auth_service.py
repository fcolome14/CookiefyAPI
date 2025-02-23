import secrets
from string import digits
from sqlalchemy.orm import Session
from sqlalchemy import and_, exists
from app.models.user import User
from abc import ABC, abstractmethod

class AuthCode(ABC):
    @abstractmethod
    def generate_code(self, db: Session) -> str:
        pass

class GenerateAuthCode(AuthCode):
    def __init__(self, length=6, max_attempts=10):
        self.length = length
        self.max_attempts = max_attempts

    async def generate_code(self, db: Session) -> str:
        """Generate a unique authentication code."""
        for _ in range(self.max_attempts):
            validation_code = await self._generate_random_code()
            if not await self._check_auth_code(db, validation_code):
                return {"status": "success", "message": validation_code}
        
        return {"status": "error", "message": "Failed to generate a unique authentication code after multiple attempts."}

    async def _generate_random_code(self) -> str:
        """Generate a random code using `secrets` for security."""
        return "".join(secrets.choice(digits) for _ in range(self.length))

    async def _check_auth_code(self, db: Session, code: str) -> bool:
        """Check if the generated code already exists."""
        return db.query(exists().where(User.code == code)).scalar()