import sqlite3

def get_file_id(connection: sqlite3.Connection, fen: str):
    cursor = connection.cursor()

    cursor.execute('''SELECT file_id FROM telegramImageId WHERE fen = ? LIMIT 1''', (fen,))
    file_id = cursor.fetchone()

    return None if file_id is None else file_id[0]


def add_file_id(connection: sqlite3.Connection, fen: str, file_id: str):
    cursor = connection.cursor()

    cursor.execute('''INSERT INTO telegramImageId (fen, file_id) VALUES (?, ?) ON CONFLICT DO NOTHING''', (fen, file_id))
    connection.commit()

