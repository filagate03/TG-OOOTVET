import os
import sqlite3

db_path = 'bot.db'
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Удалена старая база: {db_path}")
    except Exception as e:
        print(f"Ошибка удаления базы: {e}. Закрой все программы, использующие bot.db")

print("Создание чистой базы данных...")
os.system("python init_db.py")
print("Готово! Теперь база абсолютно чистая и со всеми колонками.")