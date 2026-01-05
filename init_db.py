"""Database initialization script."""
import asyncio
import sqlite3
import os
from backend.db.database import init_db, engine
from backend.models import Project, User, FunnelStep, MediaFile, Broadcast, Base


async def main():
    """Initialize the database."""
    print("[DB] Initializing database...")
    
    # 1. Create tables if they don't exist
    await init_db()
    
    # 2. Manual migration for existing databases
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot.db')
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Check if admin_id exists in projects
            cursor.execute("PRAGMA table_info(projects)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'admin_id' not in columns:
                print("[DB] Adding missing admin_id column to projects table...")
                cursor.execute("ALTER TABLE projects ADD COLUMN admin_id BIGINT DEFAULT 0")
                conn.commit()
                print("[OK] Column added!")
            
            conn.close()
        except Exception as e:
            print(f"[!] Migration warning: {e}")

    print("[OK] Database is ready!")
    print("[DB] Database file: bot.db")


if __name__ == "__main__":
    asyncio.run(main())
