from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.user import User
from typing import Optional
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    """Interface for user repository operations"""
    
    @abstractmethod
    def get_user_by_email_or_username(self, email: str, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def add_user(self, user: User) -> User:
        pass
    
    @abstractmethod
    def update_user(self, user: User) -> User:
        pass

class UserRepository(IUserRepository):
    """Repository for user-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email_or_username(self, email: str, username: str) -> User | None:
        """Fetch a user by email or username."""
        if email:
            return (
                self.db.query(User)
                .filter(User.email == email)
                .first()
            )
        return (
                self.db.query(User)
                .filter(User.username == username)
                .first()
            )
    
    def add_user(self, user: User) -> User | None:
        """Fetch a user by email or username."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user(self, user: User) -> User | None:
        """Update a user record."""
        self.db.commit()
        self.db.refresh(user)
        return user
