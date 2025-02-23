from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead
from app.db.session import get_db
from app.schemas.responses import SuccessResponse
#from app.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=SuccessResponse, status_code=status.HTTP_202_ACCEPTED)
#@limiter.limit("3/minute")
def login(db: Session = Depends(get_db), user_credentials: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    
    return SuccessResponse(
            status="success",
            message="OK",
            data="TEST",
            meta={
                "request_id": request.headers.get("request-id", "default_request_id"),
                "client": request.headers.get("client-type", "unknown"),
            },
        )