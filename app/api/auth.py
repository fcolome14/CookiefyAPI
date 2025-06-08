from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.schemas.user import VerifyCodeRequest, NewPasswordRequest
from app.services.auth_service import (
    AuthCodeDecoder, 
    AuthUserCredentials, 
    JWTTokenValidator,
    RecoveryAuthCode)
from app.utils.date_time import TimeUtils
from app.repositories.user_repo import UserRepository
from fastapi.templating import Jinja2Templates
from app.core.i18n import translate
from app.core.config import settings
from slowapi.util import get_remote_address
from app.core.exceptions import limiter
from app.api.users import get_user_service
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="app/template")

@router.post("/login", response_model=SuccessResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/minute", key_func=get_remote_address)
def login(db: Session = Depends(get_db), user_credentials: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    user_repo = UserRepository(db)
    auth_credentials = AuthUserCredentials(user_repo)
    result = auth_credentials.validate_credentials(None, user_credentials.username, user_credentials.password)
    
    if result["status"] == "success":
        jwt = result["message"]["token"]
        user: User = result["message"]["user"]
        
        return SuccessResponse(
                message="Login succeed",
                data={
                    "token": jwt, 
                    "id": user.id,
                    "name": user.name, 
                    "username": user.username,
                    "email": user.email
                    },
                meta={
                    "request_id": request.headers.get("request-id", "default_request_id"),
                    "client": request.headers.get("client-type", "unknown"),
                },
            )
    return ErrorResponse(
                message="Login failed",
                meta={
                    "request_id": request.headers.get("request-id", "default_request_id"),
                    "client": request.headers.get("client-type", "unknown"),
                },
            )

@router.get("/token", status_code=status.HTTP_202_ACCEPTED)
async def email_code_validation(token: str, db: Session = Depends(get_db), request: Request = None, _=Depends(translate)):
    _ = _  # Get the translation function
    
    user_repo = UserRepository(db)
    token_validator = JWTTokenValidator(user_repo)
    
    user_language = request.headers.get("Accept-Language", "en").split(",")[0].strip()
    request.state.language = user_language
    
    decoder = AuthCodeDecoder(validator=token_validator, db=db)
    result = decoder.decode_and_validate(token)
    if result["status"] == "success":
        success = True
    else:
        success = False
    
    try:
        return templates.TemplateResponse(
        "validation_result.html",
        {
            "request": request,
            "message": _("Your account has been successfully verified.") if success else _("Verification failed."),
            "success": success,
            "email": settings.email,
            "_": _
        }
    )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found.")
    except IOError:
        raise HTTPException(status_code=500, detail="Failed to read template.")
    
@router.post("/verify-code", status_code=status.HTTP_202_ACCEPTED)
async def app_code_validation(user_recovery: VerifyCodeRequest, db: Session = Depends(get_db), request: Request = None):
    user_repo = UserRepository(db)
    time_utils = TimeUtils()
    if RecoveryAuthCode(user_repo, time_utils).validate_recovery_code(user_recovery.email, user_recovery.code):
        return SuccessResponse(
                    message="Account validated",
                    meta={
                        "request_id": request.headers.get("request-id", "default_request_id"),
                        "client": request.headers.get("client-type", "unknown"),
                    },
                )
    return ErrorResponse(
                    message="Expired code",
                    meta={
                        "request_id": request.headers.get("request-id", "default_request_id"),
                        "client": request.headers.get("client-type", "unknown"),
                    },
                )

@router.post("/user", response_model=SuccessResponse, status_code=status.HTTP_202_ACCEPTED)
async def password_code(
    user: NewPasswordRequest,
    user_service: UserService = Depends(get_user_service), 
    request: Request = None):
    
    result = await user_service.auth_user(user_email=user.email)
    if result["status"] == "success":
        return SuccessResponse(
                message="Login succeed",
                data="Waiting for account validation",
                meta={
                    "request_id": request.headers.get("request-id", "default_request_id"),
                    "client": request.headers.get("client-type", "unknown"),
                },
            )
    return ErrorResponse(
                message="Login failed",
                meta={
                    "request_id": request.headers.get("request-id", "default_request_id"),
                    "client": request.headers.get("client-type", "unknown"),
                },
            )