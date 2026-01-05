"""Projects API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from backend.db.database import get_db
from backend.models.project import Project
from backend.models.user import User
from backend.models.funnel import FunnelStep
from backend.models.media import MediaFile, funnel_media_association
from backend.models.broadcast import Broadcast
from backend.schemas.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
async def get_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects."""
    result = await db.execute(select(Project).order_by(Project.id.desc()))
    projects = result.scalars().all()
    return projects


@router.post("", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new project."""
    # Check if token already exists
    existing = await db.execute(
        select(Project).where(Project.bot_token == project.bot_token)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bot token already exists")
    
    db_project = Project(
        name=project.name,
        bot_token=project.bot_token,
        admin_id=project.admin_id or 0
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific project."""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a project and all related data."""
    # Check if project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete related data in correct order (due to foreign keys)
    # 1. Delete funnel_media_association entries
    await db.execute(
        delete(funnel_media_association).where(
            funnel_media_association.c.funnel_step_id.in_(
                select(FunnelStep.id).where(FunnelStep.project_id == project_id)
            )
        )
    )
    
    # 2. Delete funnel steps
    await db.execute(delete(FunnelStep).where(FunnelStep.project_id == project_id))
    
    # 3. Delete media files
    await db.execute(delete(MediaFile).where(MediaFile.project_id == project_id))
    
    # 4. Delete users
    await db.execute(delete(User).where(User.project_id == project_id))
    
    # 5. Delete broadcasts
    await db.execute(delete(Broadcast).where(Broadcast.project_id == project_id))
    
    # 6. Delete the project itself
    await db.delete(project)
    await db.commit()
    
    print(f"[DEL] Project {project_id} deleted with all related data")
    return {"message": "Project deleted successfully"}
