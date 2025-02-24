from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.services.auth_service import NumericAuthCode, AuthCodeManager
from app.utils.date_time import TimeUtils
from app.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to provide UserService with necessary dependencies."""
    code_strategy = NumericAuthCode(length=6)
    auth_service = AuthCodeManager(strategy=code_strategy, db=db)
    time_utils = TimeUtils()
    return UserService(db, auth_service, time_utils)

@router.post("/create", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user: UserCreate,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    """Endpoint to create a new user."""
    user_result = await user_service.create_user(user)

    if user_result["status"] == "error":
        return ErrorResponse(
            message="Failed to create user. Email or username may already exist.",
            meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
        )
    
    user: User = user_result["message"]
    return SuccessResponse(
        message="Account created successfully.",
        data={
            "email": user.email,
            "username": user.username,
        },
        meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
    )