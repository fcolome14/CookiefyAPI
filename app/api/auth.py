from fastapi import APIRouter, Depends, Request, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.responses import SuccessResponse
from app.services.auth_service import AuthCodeDecoder, JWTTokenValidator
from app.repositories.user_repo import UserRepository
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

@router.get("/token", response_model=SuccessResponse, status_code=status.HTTP_202_ACCEPTED)
#@limiter.limit("3/minute")
def code_validation(token: str, db: Session = Depends(get_db), request: Request = None):
    
    user_repo = UserRepository(db)
    token_validator = JWTTokenValidator(user_repo)
    
    decoder = AuthCodeDecoder(validator=token_validator, db=db)
    result = decoder.decode_and_validate(token)
    
    return SuccessResponse(
            status="success",
            message=result,
            data="TEST",
            meta={
                "request_id": request.headers.get("request-id", "default_request_id"),
                "client": request.headers.get("client-type", "unknown"),
            },
        )
