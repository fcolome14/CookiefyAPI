from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, select, insert, delete
from app.models.lists import List
from app.models.site import Site
from app.models.user import User
from app.models.associations import list_site_association
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
    
    def check_sites_id(self, sites_id: list[int]) -> bool | None:
        """Fetch all sites from their ids."""
        existing_ids = (
            self.db.query(Site.id)
            .filter(Site.id.in_(sites_id))
            .all()
            )
        
        found_ids = {id_tuple[0] for id_tuple in existing_ids}
        return set(sites_id) == found_ids
    
    def get_site_ids_from_list(self, list_id: int) -> list[int]:
        """Fetch site IDs directly from list_site_association table."""
        stmt = select(list_site_association.c.site_id).where(
            list_site_association.c.list_id == list_id
        )
        result = self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    def update_list_site_association(self, list_id: int, new_site_ids: list[int]) -> bool:
        """Update the list_site_association table for a given list_id."""
        try:
            # Step 1: Delete existing site associations for the list
            # delete_stmt = delete(list_site_association).where(
            #     list_site_association.c.list_id == list_id
            # )
            # self.db.execute(delete_stmt)

            if new_site_ids:
                insert_values = [
                    {"list_id": list_id, "site_id": site_id}
                    for site_id in new_site_ids
                ]
                insert_stmt = insert(list_site_association).values(insert_values)
                self.db.execute(insert_stmt)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print("Error updating list_site_association for list %d: %s", list_id, e)
            return False


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
