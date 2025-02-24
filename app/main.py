from fastapi import FastAPI
from app.api import users, auth
from app.db.session import Base, engine
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cookiefy API")

#Static HTML templates
app.mount("/static", StaticFiles(directory="app/tmp"), name="static")
templates = Jinja2Templates(directory="app/tmp")

# Include routers
app.include_router(users.router)
app.include_router(auth.router)
