"""
TG-Otvet: Main Launcher
Запускает Backend API с встроенным Bot Manager.
"""
import asyncio
import sys
import os
import sqlite3
import json
from datetime import datetime
from contextlib import asynccontextmanager

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


# Global bot tasks and instances
bot_tasks = {}
bot_instances = {}  # Store bot instances for broadcasts


def log(message: str, level: str = "INFO"):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"INFO": "[INFO]", "SUCCESS": "[OK]", "WARNING": "[!]", "ERROR": "[X]"}
    print(f"[{timestamp}] {symbols.get(level, '[INFO]')} {message}")


def create_start_handler(project_id: int):
    """Create start command handler for specific project."""
    from aiogram.types import Message
    
    db_path = os.path.join(BASE_DIR, 'bot.db')
    
    async def cmd_start(message: Message):
        """Handle /start command - register user without sending message."""
        user = message.from_user
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute(
            "SELECT id, status FROM users WHERE telegram_id = ? AND project_id = ?",
            (user.id, project_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing user - reactivate if blocked
            cursor.execute("""
                UPDATE users SET 
                    username = ?, 
                    first_name = ?, 
                    last_name = ?,
                    status = 'ACTIVE',
                    funnel_step = 0,
                    funnel_step_sent_at = NULL,
                    updated_at = ?
                WHERE id = ?
            """, (user.username, user.first_name, user.last_name, now, existing[0]))
            conn.commit()
            conn.close()
            print(f"[User] {user.id} ({user.username}) restarted funnel for project {project_id}")
        else:
            # Create new user with funnel_step = 0
            cursor.execute("""
                INSERT INTO users 
                (project_id, telegram_id, username, first_name, last_name, status, funnel_step, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'ACTIVE', 0, ?, ?)
            """, (project_id, user.id, user.username, user.first_name, user.last_name, now, now))
            conn.commit()
            conn.close()
            print(f"[New User] {user.id} ({user.username}) registered for project {project_id}")
        
        # NO automatic message - funnel step 1 will be sent by scheduler
    
    return cmd_start


def create_callback_handler(project_id: int):
    """Create callback query handler for button presses."""
    from aiogram.types import CallbackQuery
    
    db_path = os.path.join(BASE_DIR, 'bot.db')
    
    async def handle_callback(callback: CallbackQuery):
        """Handle button presses."""
        data = callback.data
        
        if not data.startswith("btn_"):
            await callback.answer()
            return
        
        # Parse callback data: btn_{step_id}_{button_index}
        try:
            parts = data.split("_")
            step_id = int(parts[1])
            btn_index = int(parts[2])
        except:
            await callback.answer("[X] Error")
            return
        
        # Get button config
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT buttons FROM funnel_steps WHERE id = ?", (step_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            await callback.answer("[X] Button not found")
            return
        
        try:
            buttons = json.loads(result[0]) if isinstance(result[0], str) else result[0]
        except:
            await callback.answer("[X] Error")
            return
        
        # Find button by row and index
        all_buttons = []
        for btn in buttons:
            all_buttons.append(btn)
        
        if btn_index >= len(all_buttons):
            await callback.answer("[X] Button not found")
            return
        
        button = all_buttons[btn_index]
        
        if button['action'] == 'callback':
            # Send the message from button value
            await callback.message.answer(button['value'])
            await callback.answer()
        else:
            await callback.answer()
        
        print(f"[Button] {button['text']} pressed by user {callback.from_user.id}")
    
    return handle_callback


async def run_single_bot(project_id: int, project_name: str, bot_token: str):
    """Run a single bot instance."""
    from aiogram import Bot, Dispatcher, Router
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.filters import Command
    from bot.services.funnel_scheduler import FunnelScheduler
    
    log(f"Starting bot: {project_name} (ID: {project_id})", "SUCCESS")
    
    scheduler = None
    bot = None
    
    try:
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Store bot instance for broadcasts
        bot_instances[project_id] = bot
        
        # Create new dispatcher and router for this bot
        dp = Dispatcher()
        router = Router()
        
        # Register start handler
        router.message.register(create_start_handler(project_id), Command("start"))
        
        # Register callback handler for buttons
        router.callback_query.register(create_callback_handler(project_id))
        
        dp.include_router(router)
        
        scheduler = FunnelScheduler(bot, project_id)
        scheduler.start()
        
        bot_info = await bot.get_me()
        log(f"Bot @{bot_info.username} connected!", "SUCCESS")
        
        await dp.start_polling(bot)
        
    except asyncio.CancelledError:
        log(f"Bot {project_name} stopped", "WARNING")
    except Exception as e:
        log(f"Bot {project_name} error: {e}", "ERROR")
    finally:
        if project_id in bot_instances:
            del bot_instances[project_id]
        if scheduler:
            scheduler.stop()
        if bot:
            await bot.session.close()


async def bot_manager_task():
    """Background task to manage bots."""
    global bot_tasks
    
    log("Bot Manager started - auto-starting bots from database", "INFO")
    
    while True:
        try:
            db_path = os.path.join(BASE_DIR, "bot.db")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, bot_token FROM projects")
                projects = cursor.fetchall()
                conn.close()
                
                # Start new bots
                current_ids = set()
                for project_id, name, token in projects:
                    current_ids.add(project_id)
                    if project_id not in bot_tasks or bot_tasks[project_id].done():
                        task = asyncio.create_task(run_single_bot(project_id, name, token))
                        bot_tasks[project_id] = task
                
                # Stop removed bots
                for pid in list(bot_tasks.keys()):
                    if pid not in current_ids:
                        bot_tasks[pid].cancel()
                        del bot_tasks[pid]
                        log(f"Stopped bot for deleted project {pid}", "WARNING")
        
        except Exception as e:
            log(f"Bot manager error: {e}", "ERROR")
        
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    # Initialize database
    from backend.db.database import init_db
    from backend.models import Project, User, FunnelStep, MediaFile, Broadcast
    await init_db()
    log("Database initialized", "SUCCESS")
    
    # Create media directory
    media_dir = os.path.join(BASE_DIR, "media")
    os.makedirs(media_dir, exist_ok=True)
    
    # Start bot manager
    manager_task = asyncio.create_task(bot_manager_task())
    
    yield
    
    # Cleanup
    manager_task.cancel()
    for task in bot_tasks.values():
        task.cancel()


# Create FastAPI app with bot manager
from backend.api.projects import router as projects_router
from backend.api.users import router as users_router
from backend.api.funnel import router as funnel_router
from backend.api.media import router as media_router
from backend.api.broadcast import router as broadcast_router
from backend.core.config import MEDIA_DIR

app = FastAPI(
    title="TG-Otvet API",
    description="Telegram Bot Funnel System with Auto Bot Manager",
    version="1.0.0",
    lifespan=lifespan
)

from backend.core.config import CORS_ORIGINS

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

# Serve media files
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Include API routers FIRST
app.include_router(projects_router)
app.include_router(users_router)
app.include_router(funnel_router)
app.include_router(media_router)
app.include_router(broadcast_router)

# Serve frontend static files LAST (so they don't override API)
frontend_dist = os.path.join(BASE_DIR, "frontend", "dist")

if os.path.exists(frontend_dist):
    # Mount the static files directory
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # Serve index.html for root path
    @app.get("/")
    async def serve_root():
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    
    # Catch-all route for SPA (React Router)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If it's an API call that reached here, it's a real 404
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
        
        # Check if the file exists in dist
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            from fastapi.responses import FileResponse
            return FileResponse(file_path)
            
        # Otherwise serve index.html for React Router
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    
    log(f"Serving frontend from {frontend_dist}", "SUCCESS")
else:
    log("Frontend dist not found. Frontend will not be served by backend.", "WARNING")


# Export bot_instances for broadcast API
def get_bot_instance(project_id: int):
    """Get bot instance for a project."""
    return bot_instances.get(project_id)




@app.options("/{full_path:path}")
async def preflight_handler(request):
    """Handle preflight OPTIONS requests."""
    return {"detail": "OK"}


@app.get("/health")
async def health():
    return {"status": "healthy", "bots": len(bot_tasks)}


if __name__ == "__main__":
    print()
    print("=" * 50)
    print("  TG-Otvet: Telegram Bot Funnel System")
    print("=" * 50)
    print()
    print("  API:  http://localhost:8002")
    print("  Docs: http://localhost:8002/docs")
    print()
    print("  Frontend: запустите в другом терминале:")
    print("    cd frontend && npm run dev")
    print()
    print("=" * 50)
    print()
    
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )
