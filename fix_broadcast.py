#!/usr/bin/env python3

# Скрипт для исправления broadcast.py на сервере

import os

# Путь к файлу
file_path = '/tg-tgndlasdklasjdhlaksjdlasjdaslkdjl/backend/api/broadcast.py'

# Новое содержимое для строк 16-20
new_content = '''import os
DB_PATH = os.path.join(os.getcwd(), 'bot.db')
MEDIA_DIR = os.path.join(os.getcwd(), 'media')
'''

# Читаем файл
with open(file_path, 'r') as f:
    lines = f.readlines()

# Заменяем строки 16-20
lines[15:20] = [new_content]

# Записываем обратно
with open(file_path, 'w') as f:
    f.writelines(lines)

print("Файл broadcast.py исправлен!")