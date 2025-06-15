from __future__ import annotations

import chess.pgn
import sqlite3

from src.cls.openings_list import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader
    from src.cls.Opening import Opening

class Opening:
    def __init__(self, ml: 'ModuleLoader', connection: sqlite3.Connection, moves_str='', searchById=0):

        self.connection = connection
        self.cursor = connection.cursor()

        self.ml = ml

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

        if searchById != 0:
            self.cursor.execute('SELECT * FROM openings WHERE id = ? LIMIT 1', (searchById,))
            data = self.cursor.fetchone()

            if data is None:
                return
            
            self.id = data[0]
            self.name = data[1]
            self.sequence = data[2]
            self.parentId = data[3]

    
    def get_children_class(self):
        l = self.get_children_first()

        return [Opening(self.ml, self.connection, searchById=id) for id in l]
    

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

            if len(result) > 0:
                result = result[-1]

                op = self.ml.Opening.Opening(self.ml, self.connection)
                op.id = result[0]
                op.name = result[1]
                op.sequence = result[2]
                op.parentId = result[3]

                return op

            moves.pop()

        return self.ml.Opening.Opening(self.ml, self.connection)


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
        self.connection.commit()

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

        self.cursor.execute('INSERT INTO openings (id, name, sequence) VALUES (?, ?, ?) ON CONFLICT DO NOTHING', (0, '', ''))

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


    def get_opening(self, node: chess.pgn.Game) -> Opening:
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
        
        return self.ml.Opening.Opening(self.ml, self.connection, moves_str=move_str)
