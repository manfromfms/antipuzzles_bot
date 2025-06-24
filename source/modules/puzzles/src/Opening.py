from __future__ import annotations

from ...database import get_connection
from .openings_list import openings_list

import chess.pgn

class Opening:
    def __init__(self, moves_str=''):
        self.connection = get_connection()
        self.cursor = self.connection.cursor()

        self.id = 0
        self.name = ''
        self.sequence = ''
        self.parentId = 0

    @staticmethod
    def searchById(id: int) -> Opening:
        connection = get_connection()
        cursor = connection.cursor() # sqlite3.Cursor

        opening = Opening()

        if id != 0:
            cursor.execute('SELECT * FROM openings WHERE id = ? LIMIT 1', (id,))
            data = cursor.fetchone()

            if data is None:
                return Opening()
            
            opening.id = data[0]
            opening.name = data[1]
            opening.sequence = data[2]
            opening.parentId = data[3]

        return opening


    def movesFromParent(self):
        parent = Opening.searchById(id=self.parentId)

        s = self.sequence.replace(parent.sequence, '--').replace('-- ', '') if len(parent.sequence) > 0 else self.sequence

        points = s.split(' ')

        if points[0][0] not in '0123456789':
            s = parent.sequence.split(' ')[-2] + '.. ' + s

        return s

    
    def get_children_class(self):
        l = self.get_children_first()

        return [Opening.searchById(id=id) for id in l]
    

    def count_puzzles(self):
        l = self.get_children()

        self.cursor.execute(f'SELECT count(*) FROM puzzles WHERE openingId IN ({','.join('?' * len(l))})', list(l))

        return self.cursor.fetchone()[0]
    

    def count_puzzles_solved(self, userId=0):
        l = self.get_children()

        if userId == 0:
            self.cursor.execute(f'SELECT count(*) FROM puzzles WHERE EXISTS (SELECT 1 FROM played WHERE played.puzzleId = puzzles.id) AND puzzles.openingId IN ({','.join('?' * len(l))})', list(l))
        else:
            i = list(l)
            i = [userId] + i
            self.cursor.execute(f'SELECT count(*) FROM puzzles WHERE EXISTS (SELECT 1 FROM played WHERE played.puzzleId = puzzles.id AND played.userId = ?) AND puzzles.openingId IN ({','.join('?' * len(l))})', i)

        return self.cursor.fetchone()[0]
    

    def get_children_first(self):
        self.cursor.execute(f'SELECT * FROM openings WHERE parentId = ?', (self.id,))

        openings = self.cursor.fetchall()

        ids = set()

        for o in openings:
            if o[0] == 0:
                continue
            ids.add(o[0])

        return list(ids)


    def get_children(self):
        ids = set([self.id])
        result = ids

        while len(ids) > 0:
            self.cursor.execute(f'SELECT * FROM openings WHERE parentId IN ({','.join('?' * len(ids))})', list(ids))

            openings = self.cursor.fetchall()

            ids = set()

            for o in openings:
                if o[0] == 0:
                    continue
                ids.add(o[0])
                result.add(o[0])

        return list(result)


    @staticmethod
    def searchByMovesStr(moves_str: str):
        """Find opening based on PGN string of SAN moves.

        Args:
            moves_str (str): String of moves

        Returns:
            Opening: Available opening.
        """
        connection = get_connection()
        cursor = connection.cursor()

        moves = []
        moves = moves_str.split(' ')

        while len(moves) > 0:
            if len(moves) % 3 == 1:
                moves.pop()
                continue

            string = str(' '.join(moves))

            cursor.execute('SELECT * FROM openings WHERE sequence = ?', (string,))
            result = cursor.fetchall()

            if len(result) > 0:
                result = result[-1]

                op = Opening()
                op.id = result[0]
                op.name = result[1]
                op.sequence = result[2]
                op.parentId = result[3]

                return op

            moves.pop()

        return Opening()


    @staticmethod
    def setup_database_structure():
        """Create openings table if it doesn't exist."""

        connection = get_connection()
        cursor = connection.cursor()

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

        cursor.execute(create_table_sql)
        connection.commit()

        for index_stmt in index_sql:
            cursor.execute(index_stmt)

        insert_sql = """
        INSERT INTO openings (
            name,
            sequence
        ) VALUES (?, ?)
        ON CONFLICT DO NOTHING
        """

        for opening in openings_list:
            cursor.execute(insert_sql, opening)

        cursor.execute('INSERT INTO openings (id, name, sequence) VALUES (?, ?, ?) ON CONFLICT DO NOTHING', (0, '', ''))

        Opening.fix_openings_parents()

        connection.commit()


    @staticmethod
    def fix_openings_parents():
        """Loops though all openings and fixes missing parents links."""
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT id, sequence FROM openings WHERE parentId = 0')
        openings = cursor.fetchall()

        for opening in openings:
            moves = opening[1].split(' ')
            moves.pop()

            result = Opening.searchByMovesStr(' '.join(moves))
            cursor.execute('UPDATE openings SET parentId = ? WHERE id = ?', (result.id, opening[0]))


    @staticmethod
    def get_opening(node: chess.pgn.Game) -> Opening:
        """Find the deepest opening available in provided position.

        Args:
            node (chess.pgn.Game): Chess position with previous moves, leading to the beginning of the game.

        Returns:
            Opening: Available opening.
        """
        moves = []
        while node.parent is not None:
            moves.append(node.parent.board().san(node.move)) # type: ignore
            node = node.parent # type: ignore
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
        
        return Opening(moves_str=move_str)
    

    def __repr__(self):
        return (
            f"puzzles.Opening("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"sequence='{self.sequence}', "
            f"parentId={self.parentId}"
            f")"
        )
