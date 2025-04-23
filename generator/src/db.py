import sqlite3

def create_db(path):
    connection = sqlite3.connect(path)

    c = connection.cursor()

    return c