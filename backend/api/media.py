"""Media API endpoints."""
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.db.database import get_db
from backend.models.media import MediaFile
from backend.schemas.schemas import MediaFileResponse
from backend.core.config import MEDIA_DIR

router = APIRouter(prefix="/api/media", tags=["media"])

# Allowed file extensions
ALLOWED_PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}


def get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in ALLOWED_PHOTO_EXTENSIONS:
        return "photo"
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        return "video"
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


@router.get("", response_model=List[MediaFileResponse])
async def get_media_files(
    project_id: int = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all media files for a project."""
    result = await db.execute(
        select(MediaFile)
        .where(MediaFile.project_id == project_id)
        .order_by(MediaFile.created_at.desc())
    )
    files = result.scalars().all()
    return files


@router.post("/upload", response_model=MediaFileResponse)
async def upload_media(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a media file."""
    try:
        file_type = get_file_type(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    # Create project media directory
    project_media_dir = os.path.join(MEDIA_DIR, str(project_id))
    os.makedirs(project_media_dir, exist_ok=True)
    
    file_path = os.path.join(project_media_dir, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Create database record
    db_file = MediaFile(
        project_id=project_id,
        filename=unique_filename,
        original_name=file.filename,
        file_type=file_type,
        file_size=len(content)
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    
    return db_file


@router.get("/file/{project_id}/{filename}")
async def get_media_file(project_id: int, filename: str):
    """Serve a media file."""
    file_path = os.path.join(MEDIA_DIR, str(project_id), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@router.delete("/{media_id}")
async def delete_media(media_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a media file."""
    result = await db.execute(
        select(MediaFile).where(MediaFile.id == media_id)
    )
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media file not found")
    
    # Delete physical file
    file_path = os.path.join(MEDIA_DIR, str(media.project_id), media.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    await db.delete(media)
    await db.commit()
    return {"message": "Media file deleted successfully"}
