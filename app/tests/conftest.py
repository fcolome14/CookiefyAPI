import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.config import settings

# Create a test database engine
DATABASE_URL = (
    f"postgresql://{settings.database_username}:"
    f"{settings.database_password}@{settings.database_hostname}:"
    f"{settings.database_port}/{settings.database_name}"
)
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database schema once for the whole session
@pytest.fixture(scope="session")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
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
