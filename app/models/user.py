from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    code = Column(Integer, unique=True, index=True)
    code_exp = Column(String, unique=False, index=False)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
