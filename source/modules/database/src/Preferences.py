import sqlite3

from .database import get_connection


class Preferences:
    def __init__(self, searchByUserId=0):

        self.connection = get_connection()
        self.cursor = self.connection.cursor()
        
        self.id = 0
        self.userId = searchByUserId

        self.rating_difference = 0

        self.openingId = 0
        self.opening_explicit = 0

        self.lang = ''

        if searchByUserId != 0:
            self.cursor.execute('SELECT * FROM preferences WHERE userId=? LIMIT 1', (searchByUserId,))

            data = self.cursor.fetchone()

            if data is not None:
                self.id = data[0]
                self.userId = data[1]

                self.rating_difference = data[2]
                self.openingId = data[3]
                self.opening_explicit = data[4]

                self.lang = data[5]
        

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
                    opening_explicit = ?,
                    lang = ?,
                WHERE (id = ?)
            """

            # Parameters for the update query
            update_params = (
                self.rating_difference,
                self.openingId,
                self.opening_explicit,
                self.lang,
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
                opening_explicit,
                lang
            ) VALUES (?, ?, ?, ?, ?)
        """

        insert_params = (
            self.userId,
            self.rating_difference,
            self.openingId,
            self.opening_explicit,
            self.lang,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    def create_entry(self, lang="en"):
        insert_query = """
            INSERT INTO preferences (
                userId,
                lang
            ) VALUES (?, ?)
            ON CONFLICT DO NOTHING
        """

        self.lang = lang

        insert_params = (
            self.userId,
            self.lang,
        )

        self.cursor.execute(insert_query, insert_params)

        self.connection.commit()


    @staticmethod
    def setup_database_structure():
        """Create preferences table if it doesn't exist."""
        
        connection = get_connection()
        cursor = connection.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY,
            userId INTEGER NOT NULL UNIQUE REFERENCES users (id),
            rating_difference REAL DEFAULT 0,
            openingId INTEGER REFERENCES openings (id) DEFAULT 0,
            opening_explicit INTEGER DEFAULT 0,
            lang TEXT DEFAULT 'en'
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_userId_preferences ON preferences (userId)",
        ]

        cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        connection.commit()
        