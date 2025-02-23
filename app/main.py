from fastapi import FastAPI
from app.api import users, auth
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cookiefy API")

# Include routers
app.include_router(users.router)
app.include_router(auth.router)
