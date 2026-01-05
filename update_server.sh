#!/bin/bash

# 1. Обновляем код из репозитория (если используешь git)
# git pull

# 2. Активируем окружение и обновляем зависимости
source venv/bin/activate
pip install -r requirements_production.txt

# 3. Применяем изменения в БД (добавление колонки admin_id)
python migrate_db.py

# 4. Собираем фронтенд заново
cd frontend
npm install
npm run build
cd ..

# 5. Перезапускаем всё
chmod +x start_vps.sh
./start_vps.sh

echo "=========================================="
echo "Server updated and restarted!"
echo "=========================================="