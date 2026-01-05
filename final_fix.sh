#!/bin/bash
cd /tg-tgndlasdklasjdhlaksjdlasjdaslkdjl

# 1. Останавливаем всё
pkill -f gunicorn
pkill -f bot/main.py

# 2. Копируем базу из всех возможных мест в корень (на всякий случай)
cp backend/bot.db ./bot.db 2>/dev/null
cp backend/api/bot.db ./bot.db 2>/dev/null

# 3. Принудительно прописываем admin_id всем проектам, чтобы не было ошибок валидации
source venv/bin/activate
python3 -c "
import sqlite3
conn = sqlite3.connect('bot.db')
cursor = conn.cursor()
try:
    cursor.execute('ALTER TABLE projects ADD COLUMN admin_id BIGINT')
except:
    pass
cursor.execute('UPDATE projects SET admin_id = 0 WHERE admin_id IS NULL')
conn.commit()
conn.close()
print('Database fixed!')
"

# 4. Запускаем
./start_vps.sh