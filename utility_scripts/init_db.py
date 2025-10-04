import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO ingredients(name, category) VALUES (?, ?)", ('Steak', 'protein'))
cur.execute("INSERT INTO ingredients(name, category) VALUES (?, ?)", ('Chicken Thigh', 'protein'))
cur.execute("INSERT INTO ingredients(name, category) VALUES (?, ?)", ('Chicken Wings', 'protein'))
cur.execute("INSERT INTO ingredients(name, category) VALUES (?, ?)", ('Bacon', 'protein'))

connection.commit()
connection.close()
