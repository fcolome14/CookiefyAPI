
from fastapi import APIRouter, Depends, Request, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.services.post_service import PostService
from app.models.image import Image
from app.core.security import get_current_user
from app.services.auth_service import NumericAuthCode, AuthCodeManager
from app.utils.date_time import TimeUtils
from app.db.session import get_db
from io import BytesIO
from fastapi.responses import StreamingResponse, FileResponse 
from app.schemas.media import UploadImage
from fastapi import Form


router = APIRouter(prefix="/images", tags=["Images"])

def get_post_service(db: Session = Depends(get_db)) -> PostService:
    """Dependency to provide PostService with necessary dependencies."""
    code_strategy = NumericAuthCode(length=6)
    auth_service = AuthCodeManager(strategy=code_strategy, db=db)
    time_utils = TimeUtils()
    return PostService(db, auth_service, time_utils)

@router.get("/media-db/{image_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def get_image_content_database(
    request: Request,
    image_id: int,
    _: int = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """Endpoint to get an image content from a post."""

    result = await post_service.get_image(image_id)

    if result["status"] == "error":
        return ErrorResponse(
            message=result["content"],
            meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
        )
    
    image: Image = result["content"]
    return StreamingResponse(BytesIO(image.data), media_type="image/png")


@router.post("/upload-image/", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
async def upload_image(
    request: Request,
    id: int = Form(...),
    target_model: bool = Form(...),
    file: UploadFile = File(...), 
    user_id: int = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):

    result = await post_service.upload_image(file=file, target_metadata=target_model, id_metadata=id)

    if result["status"] == "error":
        return ErrorResponse(
            message=result["content"],
            meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
        )
        
    return SuccessResponse(
        message="Image uploaded",
        data={},
        meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
    )