from __future__ import annotations

import sqlite3
from ...database import get_connection


class Preferences:
    def __init__(self, id=0):
        self.connection = get_connection()
        self.cursor = self.connection.cursor()

        self.id = id
        self.playerId = 0
        # Stored as a sanitized string (e.g. tab-separated values)
        self.values = ''

        self.amount = 1


    def get_preferences(self):
        result = self.values.split('\t')

        while (len(result) < self.amount):
            result.append('')

        return result
    

    def set_preferences(self, index, value):
        temp = self.values.split('\t')

        while (len(temp) < self.amount):
            temp.append('')

        temp[index] = value
        self.values = '\t'.join(value)

        self.update_database_entry()


    @staticmethod
    def searchById(id: int) -> Preferences:
        connection = get_connection()
        cursor = connection.cursor()

        prefs = Preferences()

        if id != 0:
            cursor.execute('SELECT * FROM preferences WHERE id=? LIMIT 1', (id,))
            data = cursor.fetchone()

            if data is not None:
                prefs.id = data[0]
                prefs.playerId = data[1]
                prefs.values = data[2]

        return prefs
    

    @staticmethod
    def selectByUserId(playerId: int) -> Preferences:
        """
        Return all Preferences entries for a given playerId.
        """
        connection = get_connection()
        cursor = connection.cursor()

        results: list[Preferences] = []

        if playerId != 0:
            cursor.execute('SELECT * FROM preferences WHERE playerId=?', (playerId,))
            rows = cursor.fetchall()

            for row in rows:
                pref = Preferences()
                pref.id = row[0]
                pref.playerId = row[1]
                pref.values = row[2]
                results.append(pref)

        if len(results) == 0:
            pref = Preferences()
            pref.playerId = playerId
            pref.insert_database_entry()

        return results[0]


    def update_database_entry(self):
        """
        Update the entire preferences entry in the database.
        If it doesn't exist, insert a new one.
        """
        try:
            update_query = """
                UPDATE preferences
                SET
                    playerId = ?,
                    values_data = ?
                WHERE (id = ?)
            """

            update_params = (
                self.playerId,
                self.values,
                self.id
            )

            self.cursor.execute(update_query, update_params)

            # If no rows were updated, insert a new record
            if self.cursor.rowcount == 0:
                self.insert_database_entry()

            self.connection.commit()
        except sqlite3.IntegrityError:
            # print('Duplicate entry')
            pass


    def insert_database_entry(self):
        insert_query = """
            INSERT OR IGNORE INTO preferences (
                playerId,
                values_data
            ) VALUES (?, ?)
        """

        insert_params = (
            self.playerId,
            self.values
        )

        self.cursor.execute(insert_query, insert_params)
        self.connection.commit()

        self.id = self.cursor.lastrowid


    @staticmethod
    def setup_database_structure():
        """Create preferences table if it doesn't exist."""
        connection = get_connection()
        cursor = connection.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playerId INTEGER NOT NULL,
            values_data TEXT NOT NULL
        );
        """

        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_preferences_playerId ON preferences (playerId);"
        ]

        cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        connection.commit()


    def __repr__(self):
        return f"preferences.Preferences(id={self.id}, playerId={self.playerId}, values=\"{self.values}\")"
