from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.db.base import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("now()")
    )
