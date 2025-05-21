import sqlite3


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader


class PuzzleVote:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, userId=0, puzzleId=0):
        self.connection = connection
        self.cursor = self.connection.cursor()

        self.ml = ml
        
        self.id = 0
        self.userId = userId
        self.puzzleId = puzzleId
        self.vote = 0

        if userId != 0 and puzzleId != 0:
            self.cursor.execute('SELECT * FROM puzzle_votes WHERE userId=? AND puzzleId=?', (userId, puzzleId))

            data = self.cursor.fetchone()

            if data is None:
                self.create_entry()

                self.cursor.execute('SELECT * FROM puzzle_votes WHERE userId=? AND puzzleId=?', (userId, puzzleId))
                data = self.cursor.fetchone()

            print(data)

            self.id = data[0]
            self.vote = data[3]


    def another_vote(self, value):
        self.vote = value

        self.update_database_entry()
        

    def update_database_entry(self):
        # Somehow this function is working correctly, although I don't have any idea why...
        try:
            """
            Update the whole entry in the database.
            """

            # First try to update
            update_query = """
                UPDATE puzzle_votes
                SET 
                    vote = ?
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.vote,
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
            INSERT INTO puzzle_votes (
                userId,
                puzzleId,
                vote
            ) VALUES (?, ?, ?)
            ON CONFLICT DO NOTHING
        """

        insert_params = (
            self.userId,
            self.puzzleId,
            self.vote,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    def create_entry(self):
        insert_query = """
            INSERT INTO puzzle_votes (
                userId,
                puzzleId
            ) VALUES (?, ?)
            ON CONFLICT DO NOTHING
        """

        insert_params = (
            self.userId,
            self.puzzleId,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    def setup_database_structure(self):
        """Create puzzle_votes table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS puzzle_votes (
            id INTEGER PRIMARY KEY,
            userId INTEGER NOT NULL UNIQUE REFERENCES users (id),
            puzzleId INTEGER NOT NULL UNIQUE REFERENCES puzzles (id),
            vote REAL DEFAULT 0
        );
        """
        
        index_sql = [
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        self.connection.commit()
        