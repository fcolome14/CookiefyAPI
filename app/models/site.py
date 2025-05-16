from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.db.base import Base
from sqlalchemy.orm import relationship

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    contact = Column(String, nullable=True)

    image = Column(Integer, ForeignKey("images.id"), nullable=True)
    category = Column(Integer, ForeignKey("categories.id"), nullable=True)
    hashtags = Column(Integer, ForeignKey("hashtags.id"), nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("now()")
    )
    
    lists = relationship("List", secondary="list_site_association", back_populates="sites")
    hashtags = relationship("Hashtag", secondary="site_hashtag_association", back_populates="sites")
