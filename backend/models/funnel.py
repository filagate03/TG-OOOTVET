"""Funnel step and button models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.database import Base


class FunnelStep(Base):
    """FunnelStep model - represents a step in the message funnel."""
    __tablename__ = "funnel_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    delay_seconds = Column(Integer, nullable=False, default=0)
    content_type = Column(String(20), nullable=False)  # 'text', 'photo', 'video', 'album'
    content_text = Column(Text, nullable=True)
    # Buttons as JSON array: [{"text": "Label", "action": "url|callback", "value": "...", "row": 0}]
    buttons = Column(JSON, nullable=True, default=None)
    created_at = Column(DateTime, server_default=func.now())

    # Unique constraint for project_id + step_number
    __table_args__ = (
        UniqueConstraint('project_id', 'step_number', name='uq_project_step'),
    )

    # Relationships
    project = relationship("Project", back_populates="funnel_steps")
    media_files = relationship(
        "MediaFile",
        secondary="funnel_media_association",
        back_populates="funnel_steps"
    )

    def __repr__(self):
        return f"<FunnelStep(id={self.id}, step_number={self.step_number}, content_type='{self.content_type}')>"
