"""Funnel API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from backend.db.database import get_db
from backend.models.funnel import FunnelStep
from backend.models.media import MediaFile
from backend.schemas.schemas import FunnelStepCreate, FunnelStepUpdate, FunnelStepResponse

router = APIRouter(prefix="/api/funnel", tags=["funnel"])


@router.get("/steps", response_model=List[FunnelStepResponse])
async def get_funnel_steps(
    project_id: int = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all funnel steps for a project."""
    result = await db.execute(
        select(FunnelStep)
        .options(selectinload(FunnelStep.media_files))
        .where(FunnelStep.project_id == project_id)
        .order_by(FunnelStep.step_number)
    )
    steps = result.scalars().all()
    return steps


@router.post("/steps", response_model=FunnelStepResponse)
async def create_funnel_step(
    step: FunnelStepCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new funnel step."""
    # Check if step number already exists
    existing = await db.execute(
        select(FunnelStep)
        .where(FunnelStep.project_id == step.project_id)
        .where(FunnelStep.step_number == step.step_number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400, 
            detail=f"Step number {step.step_number} already exists for this project"
        )
    
    # Convert buttons to list of dicts
    buttons_data = None
    if step.buttons:
        buttons_data = [btn.model_dump() for btn in step.buttons]
    
    db_step = FunnelStep(
        project_id=step.project_id,
        step_number=step.step_number,
        delay_seconds=step.delay_seconds,
        content_type=step.content_type,
        content_text=step.content_text,
        buttons=buttons_data
    )
    
    # Add media files if provided
    if step.media_file_ids:
        result = await db.execute(
            select(MediaFile)
            .where(MediaFile.id.in_(step.media_file_ids))
            .where(MediaFile.project_id == step.project_id)
        )
        media_files = result.scalars().all()
        db_step.media_files = list(media_files)
    
    db.add(db_step)
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(FunnelStep)
        .options(selectinload(FunnelStep.media_files))
        .where(FunnelStep.id == db_step.id)
    )
    return result.scalar_one()


@router.put("/steps/{step_id}", response_model=FunnelStepResponse)
async def update_funnel_step(
    step_id: int,
    step_update: FunnelStepUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a funnel step."""
    result = await db.execute(
        select(FunnelStep)
        .options(selectinload(FunnelStep.media_files))
        .where(FunnelStep.id == step_id)
    )
    db_step = result.scalar_one_or_none()
    if not db_step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    if step_update.delay_seconds is not None:
        db_step.delay_seconds = step_update.delay_seconds
    if step_update.content_type is not None:
        db_step.content_type = step_update.content_type
    if step_update.content_text is not None:
        db_step.content_text = step_update.content_text
    
    # Update buttons
    if step_update.buttons is not None:
        db_step.buttons = [btn.model_dump() for btn in step_update.buttons]
    
    # Update media files if provided
    if step_update.media_file_ids is not None:
        result = await db.execute(
            select(MediaFile)
            .where(MediaFile.id.in_(step_update.media_file_ids))
            .where(MediaFile.project_id == db_step.project_id)
        )
        media_files = result.scalars().all()
        db_step.media_files = list(media_files)
    
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(FunnelStep)
        .options(selectinload(FunnelStep.media_files))
        .where(FunnelStep.id == step_id)
    )
    return result.scalar_one()


@router.delete("/steps/{step_id}")
async def delete_funnel_step(
    step_id: int,
    project_id: int = Query(..., description="Project ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a funnel step."""
    result = await db.execute(
        select(FunnelStep)
        .where(FunnelStep.id == step_id)
        .where(FunnelStep.project_id == project_id)
    )
    step = result.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    await db.delete(step)
    await db.commit()
    return {"message": "Step deleted successfully"}
