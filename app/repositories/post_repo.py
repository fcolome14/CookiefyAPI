from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.lists import List
from app.models.user import User
from typing import Optional
from abc import ABC, abstractmethod
from sqlalchemy.exc import SQLAlchemyError

class IPostRepository(ABC):
    """Interface for post repository operations"""
    
    @abstractmethod
    def add_list(self, user: User) -> User:
        pass
    
    @abstractmethod
    def update_list(self, user: User) -> User:
        pass

class PostRepository(IPostRepository):
    """Repository for post-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_list_by_name(self, user_id: int, list_name: str) -> User | None:
        """Fetch a list by user_id."""
        return (
            self.db.query(List)
            .filter(and_(User.id == user_id, List.name == list_name, List.is_banned == False))  # noqa: E712
            .first()
        )
    
    def get_list_by_id(self, list_id: int) -> List | None:
        """Fetch a list by list_id."""
        return (
            self.db.query(List)
            .filter(List.id == list_id, List.is_banned == False)  # noqa: E712
            .first()
        )
    
    def add_list(self, list_obj: List) -> List | None:
        """Add a new list."""
        self.db.add(list_obj)
        self.db.commit()
        self.db.refresh(list_obj)
        return list
    
    def update_list(self, list_obj: List) -> List | None:
        """Update a list record."""
        try:
            self.db.commit()
            self.db.refresh(list_obj)
            return {"status": "success", "message": list_obj}
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Database update failed: {e}")
            return {"status": "error", "message": "Database update failed."}
