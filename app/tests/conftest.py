import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from httpx import AsyncClient
from app.core.config import settings

DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def override_get_db(db):
    def _get_db():
        yield db
    app.dependency_overrides[get_db] = _get_db

@pytest.fixture(scope="function")
def override_user():
    from app.core.security import get_current_user
    app.dependency_overrides[get_current_user] = lambda: 1

@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def async_client(override_get_db, override_user):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
