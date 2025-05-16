from sqlalchemy import Column, Integer, String
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.associations import site_hashtag_association

class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("now()")
    )
    
from app.models.site import Site  # avoid circular issues by importing here  # noqa: E402
Hashtag.sites = relationship("Site", secondary=site_hashtag_association, back_populates="hashtags")