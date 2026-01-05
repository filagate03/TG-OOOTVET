"""Media file model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.database import Base


# Association table for funnel_steps and media_files
funnel_media_association = Table(
    'funnel_media_association',
    Base.metadata,
    Column('funnel_step_id', Integer, ForeignKey('funnel_steps.id', ondelete='CASCADE'), primary_key=True),
    Column('media_file_id', Integer, ForeignKey('media_files.id', ondelete='CASCADE'), primary_key=True)
)


# Association table for broadcasts and media_files
broadcast_media_association = Table(
    'broadcast_media_association',
    Base.metadata,
    Column('broadcast_id', Integer, ForeignKey('broadcasts.id', ondelete='CASCADE'), primary_key=True),
    Column('media_file_id', Integer, ForeignKey('media_files.id', ondelete='CASCADE'), primary_key=True)
)


class MediaFile(Base):
    """MediaFile model - represents an uploaded media file."""
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=True)
    file_type = Column(String(20), nullable=False)  # 'photo', 'video'
    file_size = Column(Integer, nullable=True)
    telegram_file_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="media_files")
    funnel_steps = relationship(
        "FunnelStep",
        secondary=funnel_media_association,
        back_populates="media_files"
    )
    broadcasts = relationship(
        "Broadcast",
        secondary=broadcast_media_association,
        back_populates="media_files"
    )

    def __repr__(self):
        return f"<MediaFile(id={self.id}, filename='{self.filename}', file_type='{self.file_type}')>"
