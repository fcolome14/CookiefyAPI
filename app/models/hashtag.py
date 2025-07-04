from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.associations import site_hashtag_association

class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    score = Column(Float, nullable=True, server_default=text("0.0"))
    usage_count = Column(Integer, nullable=True, server_default=text("0"))
    image_id = Column(Integer, ForeignKey("images.id", ondelete="SET NULL"), nullable=True, server_default=text("2"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=text("now()"))

    image = relationship("Image", back_populates="hashtags")
    sites = relationship("Site", secondary=site_hashtag_association, back_populates="hashtags")

