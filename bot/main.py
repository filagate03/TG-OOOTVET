"""Telegram Bot entry point."""
import asyncio
import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.handlers import start, common
from bot.services.funnel_scheduler import FunnelScheduler


def get_bot_config():
    """Get bot configuration from database."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bot.db')
    
    if not os.path.exists(db_path):
        print(f"[X] Database not found: {db_path}")
        print("Please run: python init_db.py")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, bot_token, admin_id FROM projects LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print("[X] No project found in database!")
        print("Please create a project via the web panel first.")
        sys.exit(1)
    
    return {
        "project_id": result[0],
        "name": result[1],
        "bot_token": result[2],
        "admin_id": result[3]
    }


async def main():
    """Main bot function."""
    print("[BOT] TG-Otvet Bot Starting...")
    
    # Get config from database
    config = get_bot_config()
    print(f"[BOT] Project: {config['name']} (ID: {config['project_id']})")
    print(f"[BOT] Admin ID: {config['admin_id']}")
    
    # Initialize bot with default properties
    bot = Bot(
        token=config["bot_token"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(common.router)
    
    # Pass project_id and admin_id to handlers as middleware data
    @dp.update.outer_middleware()
    async def add_project_id(handler, event, data):
        data["project_id"] = config["project_id"]
        data["admin_id"] = config["admin_id"]
        return await handler(event, data)
    
    # Start funnel scheduler
    scheduler = FunnelScheduler(bot, config["project_id"])
    scheduler.start()
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        print(f"[OK] Bot connected: @{bot_info.username}")
        print("[OK] Bot is running! Press Ctrl+C to stop.")
        
        # Start polling
        await dp.start_polling(bot)
    
    except Exception as e:
        print(f"[X] Error: {e}")
        raise
    
    finally:
        scheduler.stop()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[BYE] Bot stopped.")
