"""User model."""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.database import Base


class User(Base):
    """User model - represents a Telegram user subscribed to a bot."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    funnel_step = Column(Integer, default=0)
    funnel_step_sent_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Unique constraint for project_id + telegram_id
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    # Relationship
    project = relationship("Project", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, funnel_step={self.funnel_step})>"
