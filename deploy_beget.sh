#!/bin/bash

echo "=========================================="
echo "DEPLOY TO BEGET - BACKEND"
echo "=========================================="

# 1. Установка зависимостей
echo "[1/3] Installing dependencies..."
pip install -r requirements_production.txt

# 2. Инициализация БД
echo "[2/3] Initializing database..."
python init_db.py

# 3. Запуск сервера
echo "[3/3] Starting server..."
gunicorn backend.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002

echo "=========================================="
echo "Backend deployed successfully!"
echo "=========================================="