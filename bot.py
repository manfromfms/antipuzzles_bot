from source.modules.database import database_init
from source.modules.puzzles import puzzles_init, Puzzle

database_init('./puzzles.db')
puzzles_init()

print(Puzzle.searchById(id=3))
