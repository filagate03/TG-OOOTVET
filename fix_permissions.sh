#!/bin/bash

# Исправляем права на vite
chmod +x frontend/node_modules/.bin/vite

# Обновляем записи в БД, где admin_id = NULL
source venv/bin/activate
python -c "
from backend.db.database import engine
from sqlalchemy import text
import asyncio

async def fix_null_admin_id():
    async with engine.begin() as conn:
        # Обновляем все NULL значения на 0
        await conn.execute(text('UPDATE projects SET admin_id = 0 WHERE admin_id IS NULL'))
        print('OK - admin_id обновлён для существующих записей')

asyncio.run(fix_null_admin_id())
"