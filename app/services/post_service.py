from sqlalchemy.orm import Session
from app.models.lists import List as ListModel
from app.models.image import Image
from app.schemas.post import (
    PostRead, 
    ListCreate, 
    ListUpdate, 
    ListDelete, 
    ListRead)
from app.services.auth_service import AuthCodeManager
from app.utils.date_time import TimeUtils
import logging
from app.repositories.post_repo import PostRepository
from abc import ABC, abstractmethod
from typing import Union, List, Optional
import os
from uuid import uuid4
from PIL import Image as PILImage
from io import BytesIO
from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "images")
MAX_IMAGE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

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
        existing_list = self.post_repo.get_list_by_list_id(list_id=list_id)
        if existing_list:
            return existing_list
        return None
    
    def _check_list_owner(self, user_id: int, list_id: Union[int, List[int]]) -> bool:
        """Check if a `list` or array of `list` objects are from a giver user."""
        fetched_list = self.post_repo.get_specific_list(user_id=user_id, list_id=list_id)
        if fetched_list:
            return fetched_list
        return None
    
    def _create_new_list(self, user_id: int, list_input: ListCreate) -> bool:
        """Creates a new list."""
        
        return self.post_repo.add_list(user_id, list_input)
    
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
    
    def _delete_list(self, list_id: Union[int, List[int]]) -> PostRead | None:
        """Delete existing list(s)."""
        
        return self.post_repo.delete_list(list_id)
    
    async def delete_list(self, user_id: int, list_delete: ListDelete) -> PostRead | None:
        """Delete existing list(s)."""
        
        fetched_list = self._check_list_object(list_delete.id)
        if not fetched_list:
            msg = "Deletion not allowed: List not found"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        fetched_list = self._check_list_owner(user_id, list_delete.id)
        if not fetched_list:
            msg = "Deletion not allowed: List does not belong to the user"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        return self._delete_list(list_delete.id)    
    
    async def update_list(self, user_id: int, list_input: ListUpdate) -> PostRead | None:
        """Update an existing list."""
        fetched_list = self._check_list_object(list_input.id)
        if not fetched_list:
            msg = f"List not found for the user {user_id}"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        return self._update_list(fetched_list, list_input)
    
    
    async def get_list(self, user_id: int) -> PostRead | None:
        fetched_lists = self.post_repo.get_lists_from_user_id(user_id=user_id)
        serialized = [ListRead.model_validate(lst) for lst in fetched_lists]
        return {"status": "success", "lists": serialized}
    
    async def get_image(self, image_id: int) -> PostRead | None:
        status, content = "error", "Not found"
        if image_id:
            content = self.post_repo.get_image(image_id)
            status = "success" if content else "error"

        return {"status": status, "content": content}
    
    async def upload_image(self, file) -> dict:
        status, content = "error", "Invalid upload"

        try:
            # Check file extension
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                return {"status": "error", "content": "Unsupported file format."}

            # Check file size (in-memory)
            file_content = await file.read()
            size_mb = len(file_content) / (1024 * 1024)
            if size_mb > MAX_IMAGE_SIZE_MB:
                return {"status": "error", "content": "File too large. Max 5MB."}

            # Load and compress using Pillow
            image_stream = BytesIO(file_content)
            image = PILImage.open(image_stream)

            # Resize or recompress if needed (optional)
            image = image.convert("RGB")  # Ensure format
            output = BytesIO()
            image.save(output, format="JPEG", optimize=True, quality=85)
            output.seek(0)

            # Save compressed image to disk
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            filename = f"{uuid4().hex}.jpg"
            file_storage = os.path.join(UPLOAD_DIR, filename) # Internal path
            file_path = f"media/{filename}" # Exposed path

            with open(file_storage, "wb") as f:
                f.write(output.read())

            # Store image metadata in DB
            image_record = Image(name=filename, path=file_path)
            content = self.post_repo.add_image_path(image_record)
            status = "success" if content else "error"

        except Exception as e:
            return {"status": "error", "content": f"Upload failed: {str(e)}"}

        return {"status": status, "content": content}
    
    def get_site(self) -> PostRead | None:
        pass