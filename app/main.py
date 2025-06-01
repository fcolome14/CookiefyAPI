# app/main.py

from fastapi import FastAPI, Request
from app.api import (users, auth, legal, posts, media)
from app.db.session import Base, engine
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from slowapi.errors import RateLimitExceeded
from app.core.exceptions import rate_limit_handler, limiter
from app.db.seed import Seed
from app.db.session import get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cookiefy API")

# Attach the limiter to the app
app.state.limiter = limiter

# Add CORS and session middlewares
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Attach the rate limit exception handler
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Expose static files for templates/assets (JS, CSS)
app.mount("/static", StaticFiles(directory="app/template"), name="static")
templates = Jinja2Templates(directory="app/template")

# Expose uploaded images
app.mount("/media", StaticFiles(directory="app/users/images"), name="media")

@app.on_event("startup")
async def seed_database():
    db = next(get_db())
    Seed.seed_data(db)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(legal.router)
app.include_router(posts.router)
app.include_router(media.router)