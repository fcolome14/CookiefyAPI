import pytest
import random
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.image import Image
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.config import settings
from app.tests.factories.dummy_data import (
    create_dummy_list,
    create_dummy_image,
    create_dummy_user,
    create_dummy_site
)
from app.db.seed import Seed

# Create test database engine
DATABASE_URL = (
    f"postgresql://{settings.database_username}:"
    f"{settings.database_password}@{settings.database_hostname}:"
    f"{settings.database_port}/{settings.database_name}_test"
)
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 1. Build schema & seed ALL data ONCE
# 1. Set up schema and global seed ONCE
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    Seed.seed_data(db)

    for i in range(3):
        db.add(create_dummy_user(i))
    for i in range(1, 3):
        db.add(create_dummy_image(i))
    for i in range(1, 3):
        db.add(create_dummy_site(i, image_id=1, category_id=1))
    for i in range(3):
        db.add(create_dummy_list(i, user_id=1))

    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

# 2. Create a fresh DB session per test
@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# 3. Override FastAPI DB dependency per test
@pytest.fixture(scope="function")
def override_get_db(db_session):
    def _get_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_db

# 4. Override user
@pytest.fixture(scope="function")
def override_user():
    from app.core.security import get_current_user
    app.dependency_overrides[get_current_user] = lambda: 1

# 5. Ensure clean override state
@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()

# 6. Test client (per test)
@pytest.fixture(scope="function")
def client(override_get_db, override_user):
    with TestClient(app) as test_client:
        yield test_client
