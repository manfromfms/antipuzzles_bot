import sqlite3


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader


class Preferences:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, searchByUserId=0):

        self.connection = connection
        self.cursor = self.connection.cursor()

        self.ml = ml
        
        self.id = 0
        self.userId = searchByUserId

        self.rating_difference = 0

        self.openingId = 0
        self.opening_explicit = 0

        if searchByUserId != 0:
            self.cursor.execute('SELECT * FROM preferences WHERE userId=? LIMIT 1', (searchByUserId,))

            data = self.cursor.fetchone()

            if data is not None:
                self.id = data[0]
                self.userId = data[1]

                self.rating_difference = data[2]
                self.openingId = data[3]
                self.opening_explicit = data[4]
        

    def update_database_entry(self):
        # Somehow this function is working correctly, although I don't have any idea why...
        try:
            """
            Update the whole entry in the database.
            """

            # First try to update
            update_query = """
                UPDATE preferences
                SET 
                    rating_difference = ?,
                    openingId = ?,
                    opening_explicit = ?
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.rating_difference,
                self.openingId,
                self.opening_explicit,
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
            INSERT INTO preferences (
                userId,
                rating_difference,
                openingId,
                opening_explicit
            ) VALUES (?, ?, ?, ?)
        """

        insert_params = (
            self.userId,
            self.rating_difference,
            self.openingId,
            self.opening_explicit,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    def create_entry(self):
        insert_query = """
            INSERT INTO preferences (
                userId
            ) VALUES (?)
            ON CONFLICT DO NOTHING
        """

        insert_params = (
            self.userId,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    def setup_database_structure(self):
        """Create preferences table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY,
            userId INTEGER NOT NULL UNIQUE REFERENCES users (id),
            rating_difference REAL DEFAULT 0,
            openingId INTEGER REFERENCES openings (id) DEFAULT 0,
            opening_explicit INTEGER DEFAULT 0
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_userId_preferences ON preferences (userId)",
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        self.connection.commit()
        