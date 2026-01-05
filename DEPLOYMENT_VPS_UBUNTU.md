# Деплой на VPS (Ubuntu 24.04)

## 1. Подключение
```bash
ssh root@82.202.128.109
# Пароль: wrFNjB*9*5Yh
```

## 2. Установка зависимостей на сервере
```bash
apt update && apt install -y python3-pip python3-venv nginx git

# Клонируем проект (если ещё не клонирован)
cd /var/www
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git tg-bot
cd tg-bot
```

## 3. Настройка Backend (.env)
Создай файл `.env` в корне проекта:
```env
# Бот
BOT_TOKEN= твой_токен_бота_от_@BotFather
ADMIN_ID= твой_телеграм_id

# База данных
DATABASE_URL=sqlite+aiosqlite:///./bot.db

# URL для CORS (фронтенд, который будет на этом же домене)
FRONTEND_URL=http://82.202.128.109

# Для вебхуков (IP или домен сервера)
WEBAPP_URL=http://82.202.128.109:8002
```

## 4. Установка Python зависимостей
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# Исправляем версию cryptography для Python 3.12
sed -i 's/cryptography==.*/cryptography>=43.0.0/' requirements.txt
pip install -r requirements.txt
```

## 5. Запуск Backend (Gunicorn)
Создадим systemd сервис для автозапуска:
```bash
nano /etc/systemd/system/tg-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Bot Backend
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/tg-bot
Environment="PATH=/var/www/tg-bot/.venv/bin"
ExecStart=/var/www/tg-bot/.venv/bin/gunicorn backend.main:app --workers 4 --bind 127.0.0.1:8002 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable tg-bot
systemctl start tg-bot
systemctl status tg-bot  # Проверка статуса
```

## 6. Настройка Frontend
Настраиваем URL API на локальный адрес бэкенда:
```bash
cd frontend
npm install
```

**Важно:** В файле `frontend/src/lib/api.js` должен быть правильный URL.
Для продакшена используй относительный путь `/api`, так как Nginx будет проксировать.

## 7. Сборка Frontend
```bash
npm run build
```
Файлы появятся в папке `frontend/dist`.

## 8. Настройка Nginx
Настраиваем Nginx как единую точку входа:
```bash
nano /etc/nginx/sites-available/tg-bot
```

Содержимое:
```nginx
server {
    listen 80;
    server_name 82.202.128.109; # Или твой домен

    # Статика фронтенда
    location / {
        root /var/www/tg-bot/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Проксирование API на бэкенд
    location /api/ {
        proxy_pass http://127.0.0.1:8002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Проксирование медиафайлов
    location /media/ {
        alias /var/www/tg-bot/media/;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/tg-bot /etc/nginx/sites-enabled/
nginx -t  # Проверка конфига
systemctl reload nginx
```

## 9. Настройка Firewall (если есть)
```bash
ufw allow 80
ufw allow 443
```

## Итог
- Бэкенд работает внутри на `127.0.0.1:8002`
- Фронтенд (статика) отдаётся Nginx-ом
- Nginx проксирует `/api` запросы на бэкенд
- Всё доступно по `http://82.202.128.109`

## Как обновить
```bash
cd /var/www/tg-bot
git pull
source .venv/bin/activate
pip install -r requirements.txt

# Пересборка фронтенда
cd frontend
npm run build

# Рестарт сервисов
systemctl restart tg-bot
systemctl reload nginx