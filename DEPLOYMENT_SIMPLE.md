# Упрощенное руководство по деплою

## Бэкенд (Beget)

1. Загрузите проект на Beget
2. Установите зависимости: `pip install -r requirements_production.txt`
3. Создайте файл `.env`:
   ```
   BOT_TOKEN=ваш_токен
   DATABASE_URL=sqlite:///./bot.db
   ENVIRONMENT=production
   SECRET_KEY=ваш_секретный_ключ
   ```
4. Запустите: `gunicorn -c gunicorn.conf.py app:application`

## Фронтенд (Netlify)

1. В корне проекта создайте файл `netlify.toml`:
   ```toml
   [build]
    publish = "dist"
     command = "npm run build"
   
   [[redirects]]
     from = "/api/*"
     to = "http://ВАШ_IP_С_BEGET:8000/:splat"
     status = 200
     force = true
   ```
2. Измените `frontend/src/lib/api.js` - замените URL на пустую строку
3. Запустите сборку: `npm run build`
4. Загрузите папку `dist` на Netlify

## Всё!