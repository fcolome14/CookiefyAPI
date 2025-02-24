from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService, UserRepository
from app.services.auth_service import GenerateAuthCode
from app.utils.date_time import TimeUtils
from app.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to provide UserService with necessary dependencies."""
    auth_service = GenerateAuthCode()
    time_utils = TimeUtils()
    #user_repository = UserRepository(db)
    return UserService(db, auth_service, time_utils)

@router.post("/create", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user: UserCreate,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    """Endpoint to create a new user."""
    user_result: User = await user_service.create_user(user)

    if user_result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to create user. Email or username may already exist.",
        )

    return SuccessResponse(
        message="Account created successfully.",
        data={
            "email": user_result.email,
            "username": user_result.username,
        },
        meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
    )