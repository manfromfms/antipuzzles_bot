import sqlite3


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader


class User:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, id=0):

        self.connection = connection
        self.cursor = self.connection.cursor()

        self.ml = ml
        
        self.id = id
        self.nickname = ''
        self.elo = 1000
        self.elodev = 256
        self.pgroup = 1000
        self.current_puzzle = 1
        

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
                    elo = ?
                    dev_elo = ?,
                    pgroup = ?,
                    current_puzzle = ?
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.nickname,
                self.elo,
                self.elodev,
                self.pgroup,
                self.current_puzzle,
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
                elo,
                elodev,
                pgroup,
                current_puzzle,
            ) VALUES (?, ?, ?, ?, ?)
        """

        insert_params = (
            self.id,
            self.nickname,
            self.elo,
            self.elodev,
            self.pgroup,
            self.current_puzzle,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    def setup_database_structure(self):
        """Create users table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            nickname TEXT NOT NULL,
            elo REAL DEFAULT 1000,
            elodev REAL DEFAULT 256,
            pgroup INTEGER DEFAULT 1000,
            current_puzzle INTEGER DEFAULT 1 REFERENCES puzzles (id)
        );
        """
        
        index_sql = [
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        self.connection.commit()
        