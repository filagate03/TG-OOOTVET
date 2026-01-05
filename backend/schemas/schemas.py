"""Pydantic schemas for API validation."""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# ============== Button Schema ==============
class ButtonSchema(BaseModel):
    text: str
    action: str  # 'url' or 'callback'
    value: str   # URL or message text
    row: int = 0  # Row number for button layout


# ============== Project Schemas ==============
class ProjectCreate(BaseModel):
    name: str
    bot_token: str
    admin_id: Optional[int] = 0


class ProjectResponse(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = ""
    bot_token: Optional[str] = ""
    admin_id: Optional[int] = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== User Schemas ==============
class UserResponse(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    funnel_step: Optional[int] = 0
    funnel_step_sent_at: Optional[datetime] = None
    status: Optional[str] = "ACTIVE"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    status: str


# ============== Media File Schemas ==============
class MediaFileResponse(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    filename: Optional[str] = ""
    original_name: Optional[str] = None
    file_type: Optional[str] = ""
    file_size: Optional[int] = None
    telegram_file_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== Funnel Step Schemas ==============
class FunnelStepCreate(BaseModel):
    project_id: int
    step_number: int
    delay_seconds: int = 0
    content_type: str
    content_text: Optional[str] = None
    media_file_ids: Optional[List[int]] = None
    buttons: Optional[List[ButtonSchema]] = None


class FunnelStepUpdate(BaseModel):
    delay_seconds: Optional[int] = None
    content_type: Optional[str] = None
    content_text: Optional[str] = None
    media_file_ids: Optional[List[int]] = None
    buttons: Optional[List[ButtonSchema]] = None


class FunnelStepResponse(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    step_number: Optional[int] = 0
    delay_seconds: Optional[int] = 0
    content_type: Optional[str] = "text"
    content_text: Optional[str] = None
    buttons: Optional[List[Any]] = None
    created_at: Optional[datetime] = None
    media_files: Optional[List[MediaFileResponse]] = []

    class Config:
        from_attributes = True


# ============== Broadcast Schemas ==============
class BroadcastCreate(BaseModel):
    project_id: int
    name: str
    content_text: Optional[str] = None
    content_type: str = "text"
    media_file_ids: Optional[List[int]] = None
    target_audience: str = "all"
    scheduled_at: Optional[datetime] = None


class BroadcastUpdate(BaseModel):
    name: Optional[str] = None
    content_text: Optional[str] = None
    content_type: Optional[str] = None
    media_file_ids: Optional[List[int]] = None
    target_audience: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class BroadcastResponse(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: Optional[str] = ""
    content_text: Optional[str] = None
    content_type: Optional[str] = "text"
    target_audience: Optional[str] = "all"
    status: Optional[str] = "draft"
    scheduled_at: Optional[datetime] = None
    sent_count: Optional[int] = 0
    created_at: Optional[datetime] = None
    media_files: Optional[List[MediaFileResponse]] = []

    class Config:
        from_attributes = True
