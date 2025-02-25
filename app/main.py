from fastapi import FastAPI
from app.api import users, auth
from app.db.session import Base, engine
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cookiefy API")

# Middleware for CORS and Sessions (for language storage)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

#Static HTML templates
app.mount("/static", StaticFiles(directory="app/tmp"), name="static")
templates = Jinja2Templates(directory="app/tmp")

# Include routers
app.include_router(users.router)
app.include_router(auth.router)
