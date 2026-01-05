# Деплой на Netlify (Frontend)

## Шаг 1: Подключение репозитория

1. Зайдите на [netlify.com](https://netlify.com)
2. Нажмите "Add new site" → "Import an existing project"
3. Подключите ваш GitHub репозиторий
4. Настройки билда:
   - Build command: `npm run build`
   - Publish directory: `dist`

## Шаг 2: Настройка переменных окружения

В настройках сайта (Site settings → Environment variables) добавьте:

**Если бэкенд на Beget:**
```
VITE_API_URL=http://твой-логин.beget.tech
```

**Или используйте IP-адрес:**
```
VITE_API_URL=http://82.202.128.109
```

## Шаг 3: Деплой

Нажмите "Deploy site" - всё готово! Netlify выдаст случайный домен вида `random-name.netlify.app`