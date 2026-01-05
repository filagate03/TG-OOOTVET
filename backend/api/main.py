"""FastAPI main application."""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.db.database import init_db
from backend.api.projects import router as projects_router
from backend.api.users import router as users_router
from backend.api.funnel import router as funnel_router
from backend.api.media import router as media_router
from backend.api.broadcast import router as broadcast_router
from backend.core.config import API_HOST, API_PORT, CORS_ORIGINS, MEDIA_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    # Import models to register them
    from backend.models import Project, User, FunnelStep, MediaFile, Broadcast
    await init_db()
    print("[OK] Database initialized")
    yield


app = FastAPI(
    title="TG-Otvet API",
    description="Telegram Bot Funnel System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_origin_regex=".*",
    # Добавляем поддержку предварительных запросов
    max_age=3600,
)

# Static files for media
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")



# Include routers
app.include_router(projects_router)
app.include_router(users_router)
app.include_router(funnel_router)
app.include_router(media_router)
app.include_router(broadcast_router)

# Serve frontend static files in production
import os
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {"message": "Frontend dist not found. Run 'npm run build' in frontend folder.", "path": frontend_dist}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
