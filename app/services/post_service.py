from sqlalchemy.orm import Session
from app.models.lists import List
from app.schemas.post import PostRead, ListCreate, ListUpdate
from app.services.auth_service import AuthCodeManager
from app.utils.date_time import TimeUtils
import logging
from app.repositories.post_repo import PostRepository
from sqlalchemy.exc import IntegrityError
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class IPostService(ABC):
    """Interface service for managing posts."""

    @abstractmethod
    def create_list(self) -> PostRead | None:
        pass
    
    @abstractmethod
    def delete_list(self) -> PostRead | None:
        pass
    
    @abstractmethod
    def update_list(self) -> PostRead | None:
        pass
    
    @abstractmethod
    def get_list(self) -> PostRead | None:
        pass
    
    @abstractmethod
    def get_site(self) -> PostRead | None:
        pass
    

class PostService(IPostService):
    """Service for managing post creation."""

    def __init__(self, db: Session, auth_code_service: AuthCodeManager, time_utils: TimeUtils):
        self.db = db
        self.auth_code_service = auth_code_service
        self.time_utils = time_utils
        self.post_repo = PostRepository(db)


    async def create_list(self, user_id: int, list_input: ListCreate) -> PostRead | None:
        """Create a new list after validating input."""
        
        if self._check_list_name(user_id, list_input.name):
            msg = f"List already exists for the user {user_id}"
            logger.error(msg)
            return {"status": "error", "message": msg}

        return self._create_new_list(user_id, list_input)
    
    def _check_list_name(self, user_id: int, list_name: str) -> bool:
        """Check if a list name already exists for a given user."""
        existing_list = self.post_repo.get_list_by_name(user_id=user_id, list_name=list_name)
        if existing_list:
            return existing_list
        return None
    
    def _check_list_object(self, list_id: int) -> bool:
        """Check if a list object already exists for a given user."""
        existing_list = self.post_repo.get_list_by_id(list_id=list_id)
        if existing_list:
            return existing_list
        return None
    
    def _create_new_list(self, user_id: int, list_input: ListCreate) -> bool:
        """Creates a new list."""
        new_list = List(
            name=list_input.name,
            description=list_input.description,
            owner=user_id,
            accepts_contributions=list_input.accepts_contributions,
            is_public=list_input.is_public,
        )

        try:
            list = self.post_repo.add_list(new_list)
            logger.info("List created successfully with ID %d", list.id)
            return {"status": "success", "message": list}
        except IntegrityError:
            self.db.rollback()
            logger.error("Failed to create list: List already exists")
            return {"status": "error", "message": "Failed to create list: List already exists"}
        except Exception as exc:
            self.db.rollback()
            logger.error("Unexpected error during user creation: %s", exc)
            return {"status": "error", "message": "Unexpected error during user creation"}
    
    def _update_list(self, list_obj: List, list_new: ListUpdate) -> bool:
        """Updates a list."""
        updated = False
        result = {"status": "error", "message": None}
        
        updates = list_new.model_dump(exclude_unset=True)
        updates.pop("id", None)
        updates.pop("image", None)
        
        for field, new_value in updates.items():
            old_value = getattr(list_obj, field)
            
            if field == "sites":
                current_site_ids = {site.id for site in list_obj.sites}
                incoming_site_ids = set(new_value)
                
                if current_site_ids != incoming_site_ids:
                    pass
            
            elif old_value != new_value:
                setattr(list_obj, field, new_value)
                updated = True
        
        if updated:
            result = self.post_repo.update_list(list_obj)
            if result["status"] == "success":
                logger.info("List updated successfully with ID %d", list_obj.id)
        else:
            logger.info("No changes detected for list ID %d", list_obj.id)
            
        return {
            "status": result.get("status", "success"), 
            "updated": updated, 
            "payload": result.get("message", list_obj)
        }
                
        
    def _update_list_name():
        pass
    
    def delete_list(self) -> PostRead | None:
        pass
    
    
    async def update_list(self, user_id: int, list_input: ListUpdate) -> PostRead | None:
        """Update an existing list."""
        fetched_list = self._check_list_object(list_input.id)
        if not fetched_list:
            msg = f"List not found for the user {user_id}"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        return self._update_list(fetched_list, list_input)
    
    def get_list(self) -> PostRead | None:
        pass
    
    
    def get_site(self) -> PostRead | None:
        pass