"""Project model."""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.database import Base


class Project(Base):
    """Project model - represents a Telegram bot project."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    bot_token = Column(String(255), nullable=False, unique=True)
    admin_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="project", cascade="all, delete-orphan")
    funnel_steps = relationship("FunnelStep", back_populates="project", cascade="all, delete-orphan")
    media_files = relationship("MediaFile", back_populates="project", cascade="all, delete-orphan")
    broadcasts = relationship("Broadcast", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
