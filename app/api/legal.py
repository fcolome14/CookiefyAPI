from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.core.i18n import translate

router = APIRouter(prefix="/legal", tags=["Legal"])
templates = Jinja2Templates(directory="app/tmp")


@router.get("/terms/")
def terms_of_service(request: Request, _=Depends(translate)):
    
    user_language = request.headers.get("Accept-Language", "en").split(",")[0].strip()
    request.state.language = user_language
    
    return templates.TemplateResponse(
        "terms_of_service.html",
        {
            "request": request,
            "url": settings.domain,
            "email": settings.email,
            "company": settings.company_name,
            "company_formal": f"{settings.company_name.capitalize()} {settings.company_reg}",
            "company_address": settings.company_address,
            "company_nif": settings.company_nif,
            "_": _
        },
    )



@router.get("/privacy/")
def privacy_policy(request: Request = None, _=Depends(translate)):
    
    user_language = request.headers.get("Accept-Language", "en").split(",")[0].strip()
    request.state.language = user_language
    
    return templates.TemplateResponse(
        "privacy_policy.html",
        {"request": request, 
         "url": settings.domain, 
         "email": settings.email, 
         "company": settings.company_name, 
         "company_formal": f"{settings.company_name.capitalize()} {settings.company_reg}",
         "company_address": settings.company_address,
         "_": _
         },
    )
