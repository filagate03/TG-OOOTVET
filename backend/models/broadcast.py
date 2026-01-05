"""Broadcast model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.database import Base


class Broadcast(Base):
    """Broadcast model - represents a broadcast message."""
    __tablename__ = "broadcasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    content_text = Column(Text, nullable=True)
    content_type = Column(String(20), nullable=False)  # 'text', 'photo', 'video', 'album'
    target_audience = Column(String(20), default="all")  # 'all', 'active'
    status = Column(String(20), default="draft")  # 'draft', 'scheduled', 'sending', 'completed'
    scheduled_at = Column(DateTime, nullable=True)
    sent_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="broadcasts")
    media_files = relationship(
        "MediaFile",
        secondary="broadcast_media_association",
        back_populates="broadcasts"
    )

    def __repr__(self):
        return f"<Broadcast(id={self.id}, name='{self.name}', status='{self.status}')>"
