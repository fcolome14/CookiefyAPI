import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import random
from app.models.user import User
from app.models.image import Image
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.config import settings
from app.tests.factories.dummy_data import (
    create_dummy_list,
    create_dummy_image, 
    create_dummy_user
    )

# Create a test database engine
DATABASE_URL = (
    f"postgresql://{settings.database_username}:"
    f"{settings.database_password}@{settings.database_hostname}:"
    f"{settings.database_port}/{settings.database_name}"
)
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database schema once for the whole session
@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create dummy data
    users = []
    for i in range(5):
        user = create_dummy_user(i)
        db.add(user)
        users.append(user)

    # Create other images
    for i in range(1, 7):
        img = create_dummy_image(i)
        db.add(img)

    # Make sure IDs are assigned
    db.flush()

    for i in range(10):
        dummy_list = create_dummy_list(i, user_id=1)
        db.add(dummy_list)


    try:
        yield db
    finally:
        db.close()

# Override get_db dependency
@pytest.fixture(scope="function")
def override_get_db(db):
    def _get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = _get_db

# Override current user
@pytest.fixture(scope="function")
def override_user():
    from app.core.security import get_current_user
    app.dependency_overrides[get_current_user] = lambda: 1

# Automatically clear dependency overrides after each test
@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()

# Provide a sync test client
@pytest.fixture(scope="function")
def client(override_get_db, override_user):
    with TestClient(app) as c:
        yield c
