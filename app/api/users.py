from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import CreateUser
from app.models.user import User
from app.db.session import get_db

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service() -> CreateUser:
    return CreateUser()

@router.post("/create", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    request: Request = None,
    user_service: CreateUser = Depends(get_user_service),
):
    result = user_service.create_user(db, user)
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=result["message"],
        )

    user_data: User = result.get("data")

    return SuccessResponse(
        message="Account created successfully.",
        data={"email": user_data.email, "username": user_data.username},
        meta={
            "request_id": request.headers.get("request-id", "default_request_id"),
            "client": request.headers.get("client-type", "unknown"),
        },
    )