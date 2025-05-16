from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.db.base import Base

class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, index=True)
    owner = Column(String, ForeignKey("users.id"), nullable=True)
    description = Column(String, nullable=True)
    likes = Column(Integer, nullable=True)
    shares = Column(Integer, nullable=True)
    saves = Column(Integer, nullable=True)
    image = Column(Integer, ForeignKey("images.id"), nullable=True)
    is_banned = Column(Boolean, nullable=True)
    is_public = Column(Boolean, nullable=True)
    accepts_contributions = Column(Boolean, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("now()")
    )

    sites = relationship("Site", secondary="list_site_association", back_populates="lists")
