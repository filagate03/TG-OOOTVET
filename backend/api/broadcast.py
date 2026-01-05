"""Broadcast API endpoints."""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os

from backend.db.database import get_db
from backend.models.broadcast import Broadcast
from backend.models.user import User
from backend.models.media import MediaFile
from backend.schemas.schemas import BroadcastCreate, BroadcastUpdate, BroadcastResponse

router = APIRouter(prefix="/api/broadcasts", tags=["broadcasts"])

# Get correct path to database
import os
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, 'bot.db')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')


async def send_broadcast_messages(broadcast_id: int, project_id: int, content_text: str, content_type: str, target_audience: str):
    """Background task to send broadcast messages."""
    import sqlite3
    
    # Import here to avoid circular imports
    try:
        from run import get_bot_instance
    except ImportError:
        print("[X] Cannot import get_bot_instance")
        return
    
    print(f"[BCAST] Starting broadcast {broadcast_id}, type: {content_type}")
    
    bot = get_bot_instance(project_id)
    if not bot:
        print(f"[X] No bot instance for project {project_id}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE broadcasts SET status = 'failed' WHERE id = ?", (broadcast_id,))
        conn.commit()
        conn.close()
        return
    
    # Get users
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if target_audience == "active":
        cursor.execute(
            "SELECT id, telegram_id FROM users WHERE project_id = ? AND status = 'ACTIVE'",
            (project_id,)
        )
    else:
        cursor.execute(
            "SELECT id, telegram_id FROM users WHERE project_id = ?",
            (project_id,)
        )
    
    users = cursor.fetchall()
    print(f"[BCAST] Found {len(users)} users for broadcast")
    
    # Convert users to proper format
    user_list = [{"id": u[0], "telegram_id": u[1]} for u in users]
    
    # Create broadcast dict with required information
    broadcast = {
        "id": broadcast_id,
        "content_type": content_type,
        "content_text": content_text
    }
    
    # Use ContentSender to send the broadcast
    from bot.services.content_sender import ContentSender
    content_sender = ContentSender(bot)
    
    sent_count = await content_sender.send_broadcast(broadcast, user_list)
    
    # Update broadcast status
    cursor.execute(
        "UPDATE broadcasts SET status = 'completed', sent_count = ? WHERE id = ?",
        (sent_count, broadcast_id)
    )
    conn.commit()
    conn.close()
    
    print(f"[OK] Broadcast {broadcast_id} completed: {sent_count} messages sent")


@router.get("", response_model=List[BroadcastResponse])
async def get_broadcasts(
    project_id: int = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all broadcasts for a project."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Broadcast)
        .where(Broadcast.project_id == project_id)
        .options(selectinload(Broadcast.media_files))
        .order_by(Broadcast.created_at.desc())
    )
    broadcasts = result.scalars().all()
    return broadcasts


@router.post("", response_model=BroadcastResponse)
async def create_broadcast(
    broadcast: BroadcastCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new broadcast."""
    db_broadcast = Broadcast(
        project_id=broadcast.project_id,
        name=broadcast.name,
        content_text=broadcast.content_text,
        content_type=broadcast.content_type,
        target_audience=broadcast.target_audience,
        scheduled_at=broadcast.scheduled_at,
        status="draft"
    )
    
    if broadcast.media_file_ids:
        result = await db.execute(
            select(MediaFile).where(MediaFile.id.in_(broadcast.media_file_ids))
        )
        db_broadcast.media_files = result.scalars().all()
        
    db.add(db_broadcast)
    await db.commit()
    
    # Reload with relationships to avoid validation errors
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Broadcast)
        .where(Broadcast.id == db_broadcast.id)
        .options(selectinload(Broadcast.media_files))
    )
    return result.scalar_one()


@router.put("/{broadcast_id}", response_model=BroadcastResponse)
async def update_broadcast(
    broadcast_id: int,
    broadcast_update: BroadcastUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing broadcast."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Broadcast)
        .where(Broadcast.id == broadcast_id)
        .options(selectinload(Broadcast.media_files))
    )
    db_broadcast = result.scalar_one_or_none()
    if not db_broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    # Update fields only if they are provided in the request
    if broadcast_update.name is not None:
        db_broadcast.name = broadcast_update.name
    if broadcast_update.content_text is not None:
        db_broadcast.content_text = broadcast_update.content_text
    if broadcast_update.content_type is not None:
        db_broadcast.content_type = broadcast_update.content_type
    if broadcast_update.media_file_ids is not None:
        result = await db.execute(
            select(MediaFile).where(MediaFile.id.in_(broadcast_update.media_file_ids))
        )
        db_broadcast.media_files = result.scalars().all()
    if broadcast_update.target_audience is not None:
        db_broadcast.target_audience = broadcast_update.target_audience
    if broadcast_update.scheduled_at is not None:
        db_broadcast.scheduled_at = broadcast_update.scheduled_at
    
    await db.commit()
    await db.refresh(db_broadcast)
    return db_broadcast


@router.post("/{broadcast_id}/start", response_model=BroadcastResponse)
async def start_broadcast(
    broadcast_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start a broadcast - actually send messages to users."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Broadcast)
        .where(Broadcast.id == broadcast_id)
        .options(selectinload(Broadcast.media_files))
    )
    broadcast = result.scalar_one_or_none()
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    if not broadcast.content_text and not broadcast.media_files:
        raise HTTPException(status_code=400, detail="Broadcast has no content")
    
    # Count target users
    query = select(User).where(User.project_id == broadcast.project_id)
    if broadcast.target_audience == "active":
        query = query.where(User.status == "ACTIVE")
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    if not users:
        raise HTTPException(status_code=400, detail="No users to send broadcast to")
    
    # Update status to sending
    broadcast.status = "sending"
    broadcast.sent_count = 0
    await db.commit()
    await db.refresh(broadcast)
    
    # Add background task to actually send messages
    background_tasks.add_task(
        send_broadcast_messages,
        broadcast.id,
        broadcast.project_id,
        broadcast.content_text,
        broadcast.content_type,
        broadcast.target_audience
    )
    
    print(f"[BCAST] Starting broadcast {broadcast_id} to {len(users)} users")
    
    return broadcast


@router.post("/{broadcast_id}/resend", response_model=BroadcastResponse)
async def resend_broadcast(
    broadcast_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Resend an existing broadcast to users."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Broadcast)
        .where(Broadcast.id == broadcast_id)
        .options(selectinload(Broadcast.media_files))
    )
    broadcast = result.scalar_one_or_none()
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    if not broadcast.content_text and not broadcast.media_files:
        raise HTTPException(status_code=400, detail="Broadcast has no content")
    
    # Count target users
    query = select(User).where(User.project_id == broadcast.project_id)
    if broadcast.target_audience == "active":
        query = query.where(User.status == "ACTIVE")
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    if not users:
        raise HTTPException(status_code=400, detail="No users to send broadcast to")
    
    # Update status to sending
    broadcast.status = "sending"
    broadcast.sent_count = 0
    await db.commit()
    await db.refresh(broadcast)
    
    # Add background task to actually send messages
    background_tasks.add_task(
        send_broadcast_messages,
        broadcast.id,
        broadcast.project_id,
        broadcast.content_text,
        broadcast.content_type,
        broadcast.target_audience
    )
    
    print(f"[BCAST] Resending broadcast {broadcast_id} to {len(users)} users")
    
    return broadcast


@router.delete("/{broadcast_id}")
async def delete_broadcast(broadcast_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a broadcast."""
    result = await db.execute(
        select(Broadcast).where(Broadcast.id == broadcast_id)
    )
    broadcast = result.scalar_one_or_none()
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    await db.delete(broadcast)
    await db.commit()
    return {"message": "Broadcast deleted successfully"}
