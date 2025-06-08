from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.db.base import Base
from sqlalchemy.orm import relationship
from app.models.associations import site_hashtag_association, list_site_association
from app.models.lists import List
from app.models.image import Image

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    score = Column(Float, nullable=True, default=0.0)

    image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    image = relationship("Image", backref="sites")
    category = Column(Integer, ForeignKey("categories.id"), nullable=True)
    hashtags = relationship("Hashtag", secondary=site_hashtag_association, back_populates="sites")

    score = Column(Float, nullable=True, server_default=text("0.0"))
    click_count = Column(Integer, nullable=True, server_default=text("0"))
    lists_count = Column(Integer, nullable=True, server_default=text("0"))

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("now()")
    )
    
from app.models.hashtag import Hashtag  # noqa: E402
Site.hashtags = relationship("Hashtag", secondary=site_hashtag_association, back_populates="sites")
Site.lists = relationship("List", secondary=list_site_association, back_populates="sites")
