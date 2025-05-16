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
    likes = Column(Integer, nullable=True, default=0)
    shares = Column(Integer, nullable=True, default=0)
    saves = Column(Integer, nullable=True, default=0)
    image = Column(Integer, ForeignKey("images.id"), nullable=True, default=1)
    is_banned = Column(Boolean, nullable=True, default=False)
    is_public = Column(Boolean, nullable=True, default=True)
    accepts_contributions = Column(Boolean, nullable=True, default=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("now()")
    )

    sites = relationship("Site", secondary="list_site_association", back_populates="lists")
