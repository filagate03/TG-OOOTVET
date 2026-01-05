# Инструкция по запуску на VPS (Ubuntu 24.04)

Ты уже закинул файлы и создал виртуальное окружение. Теперь просто добей запуск.

## Шаг 1: Настройка .env
Создай файл `.env` в папке `/tg-tgndlasdklasjdhlaksjdlasjdaslkdjl/` и вставь туда это:
```bash
DATABASE_URL=sqlite+aiosqlite:///./bot.db
FRONTEND_URL=http://82.202.128.109
BACKEND_URL=http://82.202.128.109
ENVIRONMENT=production
```

## Шаг 2: Установка Node.js (для фронтенда)
Если команды `npm` нет, выполни это:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

## Шаг 3: Сборка фронтенда
Чтобы панель открывалась по ссылке `http://82.202.128.109:8002`, выполни:
```bash
cd frontend
npm install
npm run build
cd ..
```

## Шаг 4: Запуск всего софта
```bash
chmod +x start_vps.sh
./start_vps.sh
```

Теперь открывай `http://82.202.128.109:8002` — там будет и панель, и API.

## Как проверить логи?
- Посмотреть логи бота: `tail -f bot.log`
- Посмотреть логи бэкенда: `tail -f backend.log`