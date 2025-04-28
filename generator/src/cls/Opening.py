import chess.pgn
import sqlite3

from src.cls.openings_list import *

class Opening:
    def __init__(self, connection: sqlite3.Connection, moves_str=''):

        self.connection = connection
        self.cursor = connection.cursor()

        self.id = 0
        self.name = ''
        self.sequence = ''
        self.parentId = 0

        if moves_str != '':
            found_opening = self.search_opening_by_string(moves_str) 
            #self = self.search_opening_by_string(moves_str) //it does not work
            if found_opening.id != 0:
                self.id = found_opening.id
                self.name = found_opening.name
                self.sequence = found_opening.sequence
                self.parentId = found_opening.parentId

    def search_opening_by_string(self, moves_str: str):
        moves = []
        moves = moves_str.split(' ')

        while len(moves) > 0:
            if len(moves) % 3 == 1:
                moves.pop()
                continue

            string = str(' '.join(moves))

            self.cursor.execute('SELECT * FROM openings WHERE sequence = ?', (string,))
            result = self.cursor.fetchall()

            print(result)

            if len(result) > 0:
                result = result[-1]

                op = Opening(self.connection)
                op.id = result[0]
                op.name = result[1]
                op.sequence = result[2]
                op.parentId = result[3]

                return op

            moves.pop()

        return Opening(self.connection)


    def setup_database_structure(self):
        """Create openings table if it doesn't exist."""

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS openings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            sequence TEXT UNIQUE,
            parentId INTEGER REFERENCES openings(id) DEFAULT 0
        );
        """
        
        index_sql = [
            "CREATE INDEX IF NOT EXISTS idx_sequence ON openings (sequence)",
            "CREATE INDEX IF NOT EXISTS idx_parentId ON openings (parentId)",
        ]

        self.cursor.execute(create_table_sql)
        for index_stmt in index_sql:
            self.cursor.execute(index_stmt)

        insert_sql = """
        INSERT INTO openings (
            name,
            sequence
        ) VALUES (?, ?)
        ON CONFLICT DO NOTHING
        """

        for opening in openings_list:
            self.cursor.execute(insert_sql, opening)

        self.fix_openings_parents()

        self.connection.commit()

    
    def fix_openings_parents(self):
        self.cursor.execute('SELECT id, sequence FROM openings WHERE parentId = 0')
        openings = self.cursor.fetchall()

        for opening in openings:
            moves = opening[1].split(' ')
            moves.pop()

            result = self.search_opening_by_string(' '.join(moves))
            self.cursor.execute('UPDATE openings SET parentId = ? WHERE id = ?', (result.id, opening[0]))


def get_opening(node: chess.pgn.Game, connection: sqlite3.Connection) -> Opening:
    moves = []
    while node.parent is not None:
        moves.append(node.parent.board().san(node.move))
        node = node.parent
    moves.reverse()
    
    move_parts = []
    for j in range(0, len(moves), 2):
        move_number = (j // 2) + 1
        white = moves[j]
        if j + 1 < len(moves):
            black = moves[j + 1]
            move_parts.append(f"{move_number}. {white} {black}")
        else:
            move_parts.append(f"{move_number}. {white}")
    move_str = ' '.join(move_parts)

    print(move_str)
    
    return Opening(connection, moves_str=move_str)
