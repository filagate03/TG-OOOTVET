#!/bin/bash

# 1. Убиваем старые процессы, если они есть
echo "Cleaning up old processes..."
pkill -f "gunicorn"
pkill -f "bot/main.py"

# 2. Активируем виртуальное окружение
source venv/bin/activate

# 3. Запускаем Бэкенд (API) в фоне
echo "Starting Backend (API)..."
nohup gunicorn backend.api.main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002 > backend.log 2>&1 &

# 4. Запускаем Бота в фоне
echo "Starting Bot..."
nohup python bot/main.py > bot.log 2>&1 &

echo "=========================================="
echo "All systems started!"
echo "Backend log: tail -f backend.log"
echo "Bot log: tail -f bot.log"
echo "=========================================="