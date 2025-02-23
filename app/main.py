from fastapi import FastAPI
from app.api import users
from app.db.session import Base, engine

# Create DB tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Cookiefy API")

# Include routers
app.include_router(users.router, prefix="/api")
