"""Database migration script."""
import asyncio
from sqlalchemy import text
from backend.db.database import engine


async def migrate():
    """Add admin_id column to projects table."""
    async with engine.begin() as conn:
        # Check if column exists
        result = await conn.execute(
            text("SELECT sql FROM sqlite_master WHERE type='table' AND name='projects'")
        )
        schema = result.scalar()
        
        if schema and 'admin_id' not in schema:
            print("[MIGRATION] Adding admin_id column to projects...")
            await conn.execute(text("ALTER TABLE projects ADD COLUMN admin_id BIGINT"))
            print("[OK] Migration complete!")
        else:
            print("[SKIP] Column admin_id already exists or table structure is different.")


if __name__ == "__main__":
    asyncio.run(migrate())