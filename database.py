import sqlite3

class Database():

    def __init__(self):
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, statement):
        result = self.cursor.execute(statement)
        self.conn.commit()
        return result
