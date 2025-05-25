import sqlite3


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.Puzzle import Puzzle


def get_puzzle_votes(puzzle: 'Puzzle'):
    # Get the puzzle ID
    puzzle_id = puzzle.id

    # Query to get the sum of positive and negative votes
    query = """
        SELECT
            SUM(CASE WHEN vote > 0 THEN vote ELSE 0 END) AS positive_votes,
            SUM(CASE WHEN vote < 0 THEN -vote ELSE 0 END) AS negative_votes
        FROM puzzle_votes
        WHERE puzzleId = ?
    """

    # Execute the query
    cursor = puzzle.connection.cursor()
    cursor.execute(query, (puzzle_id,))
    result = cursor.fetchone()

    # If no votes are found, return -1
    if result is None or (result[0] is None and result[1] is None):
        return -1

    # Extract positive and negative votes
    positive_votes = result[0] if result[0] is not None else 0
    negative_votes = result[1] if result[1] is not None else 0

    # Calculate the rating
    if positive_votes + negative_votes == 0:
        return -1

    rating = (positive_votes - negative_votes) / (positive_votes + negative_votes)

    return rating


class PuzzleVote:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, userId=0, puzzleId=0):
        self.connection = connection
        self.cursor = self.connection.cursor()

        self.ml = ml
        
        self.id = 0
        self.userId = userId
        self.puzzleId = puzzleId
        self.vote = 0

        if self.userId != 0 and self.puzzleId != 0:
            # Select puzzle if exists, else add new entry with vote=0
            select_query = """
                SELECT id, vote FROM puzzle_votes
                WHERE userId = ? AND puzzleId = ?
                LIMIT 1
            """
            select_params = (self.userId, self.puzzleId)

            self.cursor.execute(select_query, select_params)
            result = self.cursor.fetchone()

            if result is not None:
                self.id, self.vote = result
            else:
                self.create_entry()


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
        """

        insert_params = (
            self.userId,
            self.puzzleId,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()

        # Fetch the newly inserted row to update self.id and self.vote
        select_query = """
            SELECT id, vote FROM puzzle_votes
            WHERE userId = ? AND puzzleId = ?
        """
        select_params = (self.userId, self.puzzleId)

        self.cursor.execute(select_query, select_params)
        result = self.cursor.fetchone()

        if result is not None:
            self.id, self.vote = result


    def setup_database_structure(self):
        """Create puzzle_votes table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS puzzle_votes (
            id INTEGER PRIMARY KEY,
            userId INTEGER NOT NULL REFERENCES users (id),
            puzzleId INTEGER NOT NULL REFERENCES puzzles (id),
            vote REAL DEFAULT 0
        );
        """
        
        index_sql = [
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        self.connection.commit()
        