import sqlite3

# Создаем подключение к базе данных
connection = sqlite3.connect("data.db")
cursor = connection.cursor()

# Создаем таблицу пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                    user_id INTEGER PRIMARY KEY,
                    answer1 TEXT,
                    answer2 TEXT,
                    answer3 TEXT,
                    answer4 TEXT,
                    username TEXT
                  )''')

# Создаем таблицу клиентов
cursor.execute('''CREATE TABLE IF NOT EXISTS client (
                    user_id INTEGER PRIMARY KEY
                  )''')

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()
