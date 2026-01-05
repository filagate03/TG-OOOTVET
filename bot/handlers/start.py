"""/start command handler."""
import sqlite3
import os
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command


# Get absolute path to database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'bot.db')


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, project_id: int):
    """Handle /start command - register or update user."""
    user = message.from_user
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute(
        "SELECT id, status FROM users WHERE telegram_id = ? AND project_id = ?",
        (user.id, project_id)
    )
    existing = cursor.fetchone()
    
    if existing:
        # Update existing user
        cursor.execute("""
            UPDATE users SET 
                username = ?, 
                first_name = ?, 
                last_name = ?,
                updated_at = ?
            WHERE id = ?
        """, (user.username, user.first_name, user.last_name, now, existing[0]))
        conn.commit()
        conn.close()
        
        if existing[1] == 'BLOCKED':
            await message.answer("🔓 Ваш аккаунт был разблокирован!")
        else:
            await message.answer("👋 С возвращением!")
    else:
        # Create new user with funnel_step = 0
        cursor.execute("""
            INSERT INTO users 
            (project_id, telegram_id, username, first_name, last_name, status, funnel_step, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'ACTIVE', 0, ?, ?)
        """, (project_id, user.id, user.username, user.first_name, user.last_name, now, now))
        conn.commit()
        conn.close()
        
        await message.answer("🎉 Добро пожаловать! Вы успешно подписались.")
    
    print(f"[USER] {user.id} ({user.username}) started bot for project {project_id}")
