from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.schemas.post import ListCreate, ListUpdate, ListDelete
from app.services.post_service import PostService
from app.models.lists import List
from app.models.image import Image
from app.core.security import get_current_user
from app.services.auth_service import NumericAuthCode, AuthCodeManager
from app.utils.date_time import TimeUtils
from app.db.session import get_db
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/posts", tags=["Posts"])

def get_post_service(db: Session = Depends(get_db)) -> PostService:
    """Dependency to provide PostService with necessary dependencies."""
    code_strategy = NumericAuthCode(length=6)
    auth_service = AuthCodeManager(strategy=code_strategy, db=db)
    time_utils = TimeUtils()
    return PostService(db, auth_service, time_utils)

@router.post("/create-list", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_new_list(
    list: ListCreate,
    request: Request,
    user_id: int = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):
    """Endpoint to create a new list."""
    list_result = await post_service.create_list(user_id, list)

    if list_result["status"] == "error":
        return ErrorResponse(
            message="Failed to create list. This list already exists.",
            meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
        )
    
    list: List = list_result["message"]
    return SuccessResponse(
        message="List created successfully.",
        data={
            "id": list.id,
            "name": list.name,
        },
        meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
    )


@router.put("/update-list", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def update_list(
    list: ListUpdate,
    request: Request,
    user_id: int = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):
    """Endpoint to update a list."""
    list_result = await post_service.update_list(user_id, list)

    if list_result["status"] == "error":
        return ErrorResponse(
            message=list_result["payload"],
            meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
        )
    
    list: List = list_result["payload"]
    return SuccessResponse(
        message="List updated successfully.",
        data={
            "id": list.id,
            "name": list.name,
        },
        meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
    )

@router.delete("/delete-list", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def delete_list(
    list_delete: ListDelete,
    request: Request,
    user_id: int = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):
    """Endpoint to delete lists."""
    result = await post_service.delete_list(user_id, list_delete)

    if result["status"] == "error":
        return ErrorResponse(
            message=result["message"],
            meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
        )
    
    if len(list_delete.id) > 1:
        message=f"Lists {', '.join(list_delete.id)} deleted successfully."
    else:
        message=f"List {list_delete.id} deleted successfully."  
        
    return SuccessResponse(
        message=message,
        data={},
        meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
    )

@router.get("/get-list", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def get_list(
    request: Request,
    user_id: int = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):
    """Endpoint to get all lists from a user."""
    result = await post_service.get_list(user_id)

    if result["status"] == "error":
        return ErrorResponse(
            message=result["message"],
            meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
        )
        
    return SuccessResponse(
        message=None,
        data={"lists": result["lists"]},
        meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
    )

