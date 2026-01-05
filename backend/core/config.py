"""Application configuration."""
import os

BASE_DIR = os.getcwd()

# Media upload directory
MEDIA_DIR = os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8002

# CORS settings - configurable for different environments
import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8002")

# Build CORS origins list
CORS_ORIGINS = [FRONTEND_URL]

# Add common origins for development
if os.getenv("ENVIRONMENT") != "production":
    CORS_ORIGINS.extend([
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        BACKEND_URL,
    ])
