from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    Index,
    func
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(BigInteger, primary_key=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'site', 'list', 'user', etc.
    entity_id = Column(Integer, nullable=False)
    interaction_type = Column(String(50), nullable=False)  # 'like', 'share', 'save', 'click'
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="interactions", foreign_keys=[user_id])

    __table_args__ = (
        Index("idx_user_entity_interaction", "user_id", "entity_type", "entity_id", "interaction_type"),
        Index("idx_entity_interaction_type", "entity_type", "entity_id", "interaction_type"),
    )
