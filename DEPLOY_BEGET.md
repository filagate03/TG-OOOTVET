# Деплой на Beget (Backend + Frontend)

## Шаг 1: Загрузка файлов

1. Зайдите в панель Beget → Файловый менеджер
2. Загрузите все файлы проекта в папку `public_html`
3. Убедитесь что структура такая:
   ```
   public_html/
   ├── backend/
   ├── bot/
   ├── frontend/
   ├── media/
   ├── bot.db
   ├── .env
   └── ...
   ```

## Шаг 2: Настройка окружения

1. Создайте файл `.env` в корне (через Файловый менеджер → Создать файл):
   ```bash
   DATABASE_URL=sqlite+aiosqlite:///./bot.db
   FRONTEND_URL=http://82.202.128.109
   BACKEND_URL=http://82.202.128.109
   ENVIRONMENT=production
   ```

## Шаг 3: Установка Python и зависимостей

**Важно! Копируйте только команды, без приглашения командной строки (root@...)**

Откройте терминал Beget (SSH или через панель) и выполните по очереди:

```bash
cd /tg-tgndlasdklasjdhlaksjdlasjdaslkdjl
```

```bash
python3 --version
```

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -r requirements_production.txt
```

**Если возникнет ошибка с cryptography:**
```bash
pip install --upgrade pip
pip install -r requirements_production.txt
```

```bash
python init_db.py
```

## Шаг 4: Настройка запуска бэкенда

В панели Beget → Сайты → Управление → Настройки запуска:

1. Выберите Python 3.12 (или доступную версию)
2. В поле "Команда запуска" вставьте:
   ```
   gunicorn backend.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8002
   ```
3. Нажмите "Сохранить"

## Шаг 5: Настройка проксирования

В панели Beget → Сайты → Управление → Настройки веб-сервера:

1. Добавьте правило проксирования:
   - Путь: `/api/*`
   - Адрес: `http://127.0.0.1:8002/api/*`
2. Добавьте правило для медиа:
   - Путь: `/media/*`
   - Адрес: `http://127.0.0.1:8002/media/*`
3. Нажмите "Сохранить"

## Шаг 6: Сборка фронтенда

В терминале Beget выполните:

```bash
cd /tg-tgndlasdklasjdhlaksjdlasjdaslkdjl/frontend
```

```bash
npm install
```

```bash
npm run build
```

## Шаг 7: Запуск бота

В терминале Beget выполните:

```bash
cd /tg-tgndlasdklasjdhlaksjdlasjdaslkdjl
```

```bash
source venv/bin/activate
```

```bash
python bot/main.py
```

**Для работы в фоне (через supervisor):**

Создайте файл `/etc/supervisor/conf.d/tg-bot.conf`:
```ini
[program:tg-bot]
directory=/tg-tgndlasdklasjdhlaksjdlasjdaslkdjl
command=/tg-tgndlasdklasjdhlaksjdlasjdaslkdjl/venv/bin/python bot/main.py
user=root
autostart=true
autorestart=true
```

Перезапустите supervisor:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start tg-bot
```

Готово! Откройте `http://82.202.128.109`.