#!/bin/bash

# Применяем исправление вручную (если не работает git pull)

# 1. Останавливаем сервер
pkill -f gunicorn
pkill -f bot/main.py

# 2. Скачиваем обновлённый файл с GitHub (или используй git pull)
# Если используешь git:
cd /tg-tgndlasdklasjdhlaksjdaslkdjl
git pull

# 3. Если git pull не работает, просто замени файл вручную:
# Скопируй содержимое исправленного файла backend/api/broadcast.py на сервер

# 4. Перезапускаем
./start_vps.sh

echo "Готово! Проверь создание воронок и рассылок."