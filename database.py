# file for database
import sqlite3


class DataBase:
    def __init__(self, db_path):
        self.connect = sqlite3.connect(db_path)
        self.cursor = self.connect.cursor()

    def select_with_fetchone(self, cmd):
        self.cursor.execute(cmd)
        result = self.cursor.fetchone()
        return result

    def select_with_fetchall(self, cmd):
        self.cursor.execute(cmd)
        result = self.cursor.fetchall()
        return result

    def query(self, cmd):
        self.cursor.execute(cmd)
        self.connect.commit()
        print('Request access.')
