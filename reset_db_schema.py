"""Reset database schema to match current models."""
import asyncio
import os
import sqlite3
from backend.db.database import engine
from backend.models import Base


async def reset_database():
    """Reset the database to match current models."""
    print("Resetting database schema...")
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Create all tables with current schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database schema reset successfully!")
    print("Database file: bot.db")


def reset_sqlite_schema():
    """Alternative method to reset SQLite schema directly."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bot.db')
    print(f"Resetting database schema for {db_path}...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Drop all tables except sqlite_sequence
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    conn.commit()
    conn.close()
    
    # Now recreate using SQLAlchemy
    asyncio.run(reset_database())


if __name__ == "__main__":
    reset_sqlite_schema()