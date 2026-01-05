"""Settings model for bot configuration."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.db.database import Base


class Settings(Base):
    """Global bot settings."""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_token = Column(String(255), nullable=True)
    admin_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Settings(bot_token={self.bot_token[:10]}..., admin_id={self.admin_id})>"