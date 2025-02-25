from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.responses import SuccessResponse
from app.services.auth_service import AuthCodeDecoder, JWTTokenValidator
from app.repositories.user_repo import UserRepository
from fastapi.templating import Jinja2Templates
from app.core.i18n import translate
from app.core.config import settings
#from app.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="app/tmp")

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

@router.get("/token", status_code=status.HTTP_202_ACCEPTED)
#@limiter.limit("3/minute")
async def code_validation(token: str, db: Session = Depends(get_db), request: Request = None, _=Depends(translate)):
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

