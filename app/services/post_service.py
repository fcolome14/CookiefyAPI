from sqlalchemy.orm import Session
from app.models.lists import List as ListModel
from app.models.site import Site
from app.models.image import Image
from app.schemas.post import (
    PostRead, 
    ListCreate, 
    ListUpdate, 
    ListDelete,
    ListKPIs, 
    ListRead,
    SiteRead,
    SiteKPIs)
from app.services.auth_service import AuthCodeManager
from app.utils.date_time import TimeUtils
import logging
from app.repositories.post_repo import PostRepository
from abc import ABC, abstractmethod
from typing import Union, List
import os
from uuid import uuid4
from PIL import Image as PILImage
from io import BytesIO
from sqlalchemy.ext.declarative import DeclarativeMeta
from typing import Union, List, Type
from app.algorithms import algorithm

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "users", "images")
MAX_IMAGE_SIZE_MB = 15
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
        self.score_algorithm = algorithm.Score()
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
        fetched_list = self.post_repo.get_list_by_user_id(user_id=user_id, list_id=list_id)
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
        
        result_m = self.post_repo.update_metrics(
            model=Site, 
            column_name="lists_count", 
            record_ids=incoming_site_ids,
            addition=True)

        if result_m["status"] == "error":
            return result_m

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
        
        fetched_list: ListModel = self._check_list_object(list_delete.id)
        if not fetched_list:
            msg = "Deletion not allowed: List not found"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        fetched_list = self._check_list_owner(user_id, list_delete.id)
        if not fetched_list:
            msg = "Deletion not allowed: List does not belong to the user"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        result = self._delete_list(list_delete.id)
        if result["status"] == "success":
            deleted_lists = result["content"]
            images_ids = [item.image for item in deleted_lists if item.image != 1]
            result_img = self.post_repo.delete_list_image(image_id=images_ids)
            if result_img["status"] == "error":
                pass
        
        return result
    

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
    

    async def get_nearby_lists(self, location: str) -> PostRead | None:
        # TODO: Implement location-based fetching
        fetched_lists = self.post_repo.get_nearby_lists()


    async def get_specific_list(self, list_id: int) -> PostRead | None:
        """Fetch a specific list by its ID and update visit count."""

        fetched_list = self.post_repo.get_list_by_list_id(list_id=list_id)
        if fetched_list:
            result = self.post_repo.update_metrics(ListModel, "visit_count", list_id, addition=True)

            if result["status"] == "error":
                return {"status": "error", "message": result["message"]}
            
            result = self._update_score(list_id, ListModel)
            if 'error' in result:
                return {"status": "error", "message": result['message']}
            
            return {"status": "success", "content": ListRead.model_validate(fetched_list)}
        
        return {"status": "error", "message": "List not found"}
    

    async def get_specific_site(self, site_id: int) -> PostRead | None:
        """Fetch a specific site by its ID and update click count."""

        fetched_site = self.post_repo.get_site_by_site_id(site_id=site_id)
        if fetched_site:
            result = self.post_repo.update_metrics(Site, "click_count", site_id, addition=True)

            if result["status"] == "error":
                return {"status": "error", "message": result["message"]}
            
            result = self._update_score(site_id, Site)
            if 'error' in result:
                return {"status": "error", "message": result['message']}
            
            return {"status": "success", "content": SiteRead.model_validate(fetched_site)}
        
        return {"status": "error", "message": "Site not found"}
    

    async def get_image(self, image_id: int) -> PostRead | None:
        """Fetch a specific image by its ID."""

        status, content = "error", "Not found"
        if image_id:
            content = self.post_repo.get_image(image_id)
            status = "success" if content else "error"

        return {"status": status, "content": content}
    

    async def upload_image(self, file) -> dict:
        """Upload an image file, validate it, and save it to the server."""

        status, content = "error", "Invalid upload"

        try:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                return {"status": "error", "content": "Unsupported file format."}

            file_content = await file.read()
            size_mb = len(file_content) / (1024 * 1024)
            if size_mb > MAX_IMAGE_SIZE_MB:
                return {"status": "error", "content": "File too large. Max 5MB."}

            image_stream = BytesIO(file_content)
            image = PILImage.open(image_stream)

            image = image.convert("RGB")  # Ensure format
            image = image.resize((150, 150), PILImage.LANCZOS)
            output = BytesIO()
            image.save(output, format="JPEG", optimize=True, quality=70)
            output.seek(0)

            os.makedirs(UPLOAD_DIR, exist_ok=True)
            filename = f"{uuid4().hex}.jpg"
            file_storage = os.path.join(UPLOAD_DIR, filename) # Internal path
            file_path = f"media/{filename}" # Exposed path

            with open(file_storage, "wb") as f:
                f.write(output.read())

            image_record = Image(name=filename, path=file_path)
            content = self.post_repo.add_image_path(image_record)
            status = "success" if content else "error"

        except Exception as e:
            return {"status": "error", "content": f"Upload failed: {str(e)}"}

        return {"status": status, "content": content}
    
    def _update_score(self, item_id: int, model: Type[DeclarativeMeta]) -> dict:

        if model == ListModel:
            result = self.post_repo.get_record_kpis(ListModel, item_id)
            if 'error' in result:
                return {"status": "error", "message": result['message']}
            
            score_algorithm = self.score_algorithm.compute_list_score(
                input_metrics=ListKPIs(**result['content'])
                )
            
            result = self.post_repo.update_scores(
                model=ListModel, 
                column_name="score", 
                record_id=item_id, 
                score=score_algorithm
            )

            if result['status'] == 'error':
                return {"status": "error", "message": result['message']}
            
            return result
        
        elif model == Site:
            result = self.post_repo.get_record_kpis(Site, item_id)
            if 'error' in result:
                return {"status": "error", "message": result['message']}
            
            score_algorithm = self.score_algorithm.compute_site_score(
                input_metrics=SiteKPIs(**result['content'])
                )
            
            result = self.post_repo.update_scores(
                model=Site, 
                column_name="score", 
                record_id=item_id, 
                score=score_algorithm
            )

            if result['status'] == 'error':
                return {"status": "error", "message": result['message']}
            
            return result

    def get_site(self) -> PostRead | None:
        pass