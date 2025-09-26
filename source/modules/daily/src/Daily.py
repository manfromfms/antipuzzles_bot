from __future__ import annotations

import sqlite3

from ...database import get_connection

class Daily:
    def __init__(self):
        self.connection: sqlite3.Connection = get_connection()
        self.cursor = self.connection.cursor()

        self.id = 0
        self.userId = 0

        self.streak = 0
        self.currentDayFinishTimestamp = 0
        
        self.firstTaskType = 0
        self.firstTaskMax = 0
        self.firstTaskProgress = 0
        
        self.secondTaskType = 0
        self.secondTaskMax = 0
        self.secondTaskProgress = 0
        
        self.thirdTaskType = 0
        self.thirdTaskMax = 0
        self.thirdTaskProgress = 0


    def update_database_entry(self):
        """
        Updates an existing daily entry in the database.
        If no matching entry exists, creates a new one.
        """
        try:
            # Try to update existing entry
            update_query = """
            UPDATE daily
            SET
                userId = ?,
                streak = ?,
                currentDayFinishTimestamp = ?,
                
                -- Task 1 updates
                firstTaskType = ?,
                firstTaskMax = ?,
                firstTaskProgress = ?,
                
                -- Task 2 updates
                secondTaskType = ?,
                secondTaskMax = ?,
                secondTaskProgress = ?,
                
                -- Task 3 updates
                thirdTaskType = ?,
                thirdTaskMax = ?,
                thirdTaskProgress = ?
            WHERE (id = ?)
            """
            
            update_params = (
                self.userId,
                self.streak,
                self.currentDayFinishTimestamp,
                
                # Task 1 params
                self.firstTaskType,
                self.firstTaskMax,
                self.firstTaskProgress,
                
                # Task 2 params
                self.secondTaskType,
                self.secondTaskMax,
                self.secondTaskProgress,
                
                # Task 3 params
                self.thirdTaskType,
                self.thirdTaskMax,
                self.thirdTaskProgress,
                
                self.id  # WHERE clause parameter
            )
            
            self.cursor.execute(update_query, update_params)
            
            # If no rows were updated, insert new record
            if self.cursor.rowcount == 0:
                self.insert_database_entry()
                
            self.connection.commit()
            
        except sqlite3.IntegrityError:
            # Handle duplicate entries gracefully
            pass

    def insert_database_entry(self):
        """
        Inserts a new daily entry into the database.
        If an entry with the same userId already exists, retrieves its ID.
        """
        insert_query = """
        INSERT INTO daily (
            userId,
            streak,
            currentDayFinishTimestamp,
            
            -- Task 1 fields
            firstTaskType,
            firstTaskMax,
            firstTaskProgress,
            
            -- Task 2 fields
            secondTaskType,
            secondTaskMax,
            secondTaskProgress,
            
            -- Task 3 fields
            thirdTaskType,
            thirdTaskMax,
            thirdTaskProgress
        ) VALUES (?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?
        )
        """
        
        insert_params = (
            self.userId,
            self.streak,
            self.currentDayFinishTimestamp,
            
            # Task 1 params
            self.firstTaskType,
            self.firstTaskMax,
            self.firstTaskProgress,
            
            # Task 2 params
            self.secondTaskType,
            self.secondTaskMax,
            self.secondTaskProgress,
            
            # Task 3 params
            self.thirdTaskType,
            self.thirdTaskMax,
            self.thirdTaskProgress
        )
        
        self.cursor.execute(insert_query, insert_params)
        
        self.id = self.cursor.lastrowid
        self.connection.commit()


    @staticmethod
    def searchByUserId(userId: int) -> Daily:
        daily = Daily()

        if userId != 0:
            connection = get_connection()
            cursor = connection.cursor() # sqlite3.Cursor

            cursor.execute('SELECT * FROM daily WHERE userId = ? LIMIT 1', (userId,))
            data = cursor.fetchone()

            if data is None:
                return daily
            
            daily.id = data[0]
            daily.userId = data[1]
            daily.streak = data[2]
            daily.currentDayFinishTimestamp = data[3]
            daily.firstTaskType = data[4]
            daily.firstTaskMax = data[5]
            daily.firstTaskProgress = data[6]
            daily.secondTaskType = data[7]
            daily.secondTaskMax = data[8]
            daily.secondTaskProgress = data[9]
            daily.thirdTaskType = data[10]
            daily.thirdTaskMax = data[11]
            daily.thirdTaskProgress = data[12]

        return daily


    @staticmethod
    def setup_database_structure():
        """Create daily tracking table if it doesn't exist."""
        connection = get_connection()
        cursor = connection.cursor()
        
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userId INTEGER UNIQUE REFERENCES users(id),
                streak INTEGER NOT NULL DEFAULT 0,
                currentDayFinishTimestamp INTEGER NOT NULL DEFAULT 0,
                
                -- Task 1 fields
                firstTaskType INTEGER NOT NULL DEFAULT 0,
                firstTaskMax INTEGER NOT NULL DEFAULT 0,
                firstTaskProgress INTEGER NOT NULL DEFAULT 0,
                
                -- Task 2 fields
                secondTaskType INTEGER NOT NULL DEFAULT 0,
                secondTaskMax INTEGER NOT NULL DEFAULT 0,
                secondTaskProgress INTEGER NOT NULL DEFAULT 0,
                
                -- Task 3 fields
                thirdTaskType INTEGER NOT NULL DEFAULT 0,
                thirdTaskMax INTEGER NOT NULL DEFAULT 0,
                thirdTaskProgress INTEGER NOT NULL DEFAULT 0
            );
        """
        cursor.execute(create_table_sql)
        connection.commit()