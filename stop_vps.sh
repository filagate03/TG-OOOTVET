#!/bin/bash

echo "Stopping all services..."

# 1. Останавливаем Бэкенд (gunicorn)
pkill -f "gunicorn"

# 2. Останавливаем Бота
pkill -f "bot/main.py"

# 3. Останавливаем любые другие процессы python в этой папке
pkill -f "run.py"

echo "=========================================="
echo "All services stopped!"
echo "Check with: ps aux | grep -E 'gunicorn|python'"
echo "=========================================="