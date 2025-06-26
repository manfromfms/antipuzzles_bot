from __future__ import annotations

import sqlite3

from ...database import get_connection

class User:
    def __init__(self, id=0):

        self.connection = get_connection()
        self.cursor = self.connection.cursor()
        
        self.id = id
        self.nickname = ''
        self.pgroup = 1000


    @staticmethod
    def searchById(id: int) -> User:
        connection = get_connection()
        cursor = connection.cursor()

        user = User()

        if id != 0:
            cursor.execute('SELECT * FROM users WHERE id=? LIMIT 1', (id,))

            data = cursor.fetchone()

            if data is not None:
                user.id = data[0]
                user.nickname = data[1]
                user.pgroup = data[2]

        return user


    def update_database_entry(self):
        # Somehow this function is working correctly, although I don't have any idea why...
        try:
            """
            Update the whole entry in the database.
            """

            # First try to update
            update_query = """
                UPDATE users
                SET 
                    nickname = ?,
                    pgroup = ?
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.nickname,
                self.pgroup,
                self.id  # WHERE clause parameter
            )

            self.cursor.execute(update_query, update_params)

            # If no rows were updated, insert new record
            if self.cursor.rowcount == 0:
                self.insert_database_entry()

            self.connection.commit()
        except sqlite3.IntegrityError:
            # print('Dupelicate entry')
            pass


    def insert_database_entry(self):
        insert_query = """
            INSERT INTO users (
                id,
                nickname,
                pgroup
            ) VALUES (?, ?, ?)
        """

        insert_params = (
            self.id,
            self.nickname,
            self.pgroup
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    @staticmethod
    def setup_database_structure():
        """Create users table if it doesn't exist."""
        
        connection = get_connection()
        cursor = connection.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            nickname TEXT NOT NULL,
            pgroup INTEGER DEFAULT 1000
        );
        """
        
        index_sql = [
        ]

        cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        connection.commit()


    def __repr__(self):
        return f"users.User(id={self.id}, nickname=\"{self.nickname}\", pgroup={self.pgroup})"
