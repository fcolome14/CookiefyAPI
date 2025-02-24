from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User

class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email_or_username(self, email: str, username: str) -> User | None:
        """Fetch a user by email or username."""
        return (
            self.db.query(User)
            .filter(or_(User.email == email, User.username == username))
            .first()
        )
    
    def add_user(self, user: User) -> User | None:
        """Fetch a user by email or username."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
