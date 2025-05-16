from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.db.base import Base
from sqlalchemy.orm import relationship
from app.models.associations import site_hashtag_association, list_site_association
from app.models.lists import List

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    contact = Column(String, nullable=True)

    image = Column(Integer, ForeignKey("images.id"), nullable=True)
    category = Column(Integer, ForeignKey("categories.id"), nullable=True)
    hashtags = relationship("Hashtag", secondary=site_hashtag_association, back_populates="sites")

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("now()")
    )
    
from app.models.hashtag import Hashtag  # noqa: E402
Site.hashtags = relationship("Hashtag", secondary=site_hashtag_association, back_populates="sites")
Site.lists = relationship("List", secondary=list_site_association, back_populates="sites")
