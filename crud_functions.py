import sqlite3 as sql

def initiate_db():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL
    )
    ''')

    connection.commit()
    connection.close()

def get_all_products():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Products')

    result = cursor.fetchall()
    connection.close()

    return result

def add_user(username, email, age):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)', (username, email, age, 1000))

    connection.commit()
    connection.close()

def is_included(username):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))

    result = cursor.fetchall()
    connection.close()
    if len(result) > 0:
        return True
    else:
        return False
