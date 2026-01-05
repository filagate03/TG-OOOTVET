"""Debug script to check database and API endpoints."""
import asyncio
from sqlalchemy import text
from backend.db.database import engine
import os

async def check():
    # Check which db file exists
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'bot.db')
    backend_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bot.db')
    
    print(f"DB path in broadcast.py: {db_path}")
    print(f"DB path in backend/: {backend_db_path}")
    print(f"DB exists in root: {os.path.exists(db_path)}")
    print(f"DB exists in backend/: {os.path.exists(backend_db_path)}")
    
    # Check broadcasts table
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='broadcasts'"))
        table_exists = result.scalar()
        print(f"Broadcasts table exists: {table_exists}")
        
        if table_exists:
            result = await conn.execute(text('SELECT id, project_id, name, status FROM broadcasts'))
            print('Broadcasts:')
            for row in result.fetchall():
                print(f'  id={row[0]}, project_id={row[1]}, name={row[2]}, status={row[3]}')
            
            # Check funnel_steps
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='funnel_steps'"))
            funnel_exists = result.scalar()
            print(f"Funnel_steps table exists: {funnel_exists}")
            
            if funnel_exists:
                result2 = await conn.execute(text('SELECT id, project_id, step_number FROM funnel_steps'))
                print('Funnel steps:')
                for row in result2.fetchall():
                    print(f'  id={row[0]}, project_id={row[1]}, step={row[2]}')

if __name__ == "__main__":
    asyncio.run(check())