import sqlite3
import os

class Database():

    def __init__(self):

        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        db_file = os.path.join(THIS_FOLDER, 'database.db')
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, statement, prams: tuple=()):
        result = self.cursor.execute(statement, prams)
        self.conn.commit()
        return result
