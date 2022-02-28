import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO recipes(name, notes, cuisine) VALUES (?, ?, ?)", ('Fried Chicken', 'Yummy', 'Merican'))
cur.execute("INSERT INTO ingredients(name, category) VALUES (?, ?)", ('beef', 'protein'))

connection.commit()
connection.close()
