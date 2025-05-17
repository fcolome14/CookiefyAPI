from sqlalchemy.orm import Session
from app.models.lists import List as ListModel
from app.schemas.post import PostRead, ListCreate, ListUpdate, SitesDelete
from app.services.auth_service import AuthCodeManager
from app.utils.date_time import TimeUtils
import logging
from app.repositories.post_repo import PostRepository
from sqlalchemy.exc import IntegrityError
from abc import ABC, abstractmethod
from typing import Union, List, Optional

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
    
    def _check_list_object(self, list_id: Union[int, List[int]]) -> bool:
        """Check if a `list` or array of `list` objects already exists."""
        existing_list = self.post_repo.get_list_by_id(list_id=list_id)
        if existing_list:
            return existing_list
        return None
    
    def _check_list_owner(self, user_id: int, list_id: Union[int, List[int]]) -> bool:
        """Check if a `list` or array of `list` objects are from a giver user."""
        fetched_list = self.post_repo.get_list_by_user_id(user_id=user_id, list_id=list_id)
        if fetched_list:
            return fetched_list
        return None
    
    def _create_new_list(self, user_id: int, list_input: ListCreate) -> bool:
        """Creates a new list."""
        new_list = ListModel(
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
    
    def _update_list(self, list_obj: ListModel, list_new: ListUpdate) -> dict:
        """Updates a list record, including list_site_association."""
        updated = False
        result = {"status": "error", "message": None, "payload": None}
        site_update_required = False

        updates = list_new.model_dump(exclude_unset=True)
        updates.pop("id", None)
        updates.pop("image", None)

        incoming_site_ids = set(updates.pop("sites", []))
        if not self.post_repo.check_sites_id(incoming_site_ids):
            result["payload"] = "Invalid site IDs provided"
            return result

        current_site_ids = set(self.post_repo.get_site_ids_from_list(list_obj.id))
        if current_site_ids != incoming_site_ids:
            site_update_required = True
            updated = True

        for field, new_value in updates.items():
            old_value = getattr(list_obj, field, None)
            if old_value != new_value:
                setattr(list_obj, field, new_value)
                updated = True

        if updated:
            result = self.post_repo.update_list(list_obj)

        if site_update_required:
            success = self.post_repo.update_list_site_association(
                list_id=list_obj.id,
                new_site_ids=list(incoming_site_ids)
            )
            if not success:
                result = {
                    "status": "error",
                    "message": "Failed to update site associations"
                }

        if result["status"] == "success":
            logger.info("List updated successfully with ID %d", list_obj.id)
        elif not updated:
            logger.info("No changes detected for list ID %d", list_obj.id)

        return {
            "status": result.get("status", "success"),
            "updated": updated,
            "payload": result.get("message", list_obj),
        }
    
    def _delete_list(self, sites_id: List[int]) -> PostRead | None:
        """Delete existing site(s)."""
        
        return self.post_repo.delete_list(user_id, list_input.id)
    
    def delete_list(self, user_id: int, sites_delete: SitesDelete) -> PostRead | None:
        """Delete existing list(s)."""
        fetched_list = self._check_list_object(sites_delete.id)
        if not fetched_list:
            msg = "List not found"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        fetched_list = self._check_list_owner(user_id, sites_delete.id)
        if not fetched_list:
            msg = "Deletion not allowed: List does not belong to the user"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        return self._delete_list(sites_delete.sites)
    
    
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