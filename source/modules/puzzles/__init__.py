"""
This module contains puzzle classes:
- Game
- Opening
- Puzzle
- Solution
- Theme

Module requirements:
- database
"""

from .src.Game import Game
from .src.Opening import Opening
from .src.Puzzle import Puzzle
from .src.extend_Solution import Solution
from .src.Theme import Theme

def puzzles_init():
    Game.setup_database_structure()
    Opening.setup_database_structure()
    Puzzle.setup_database_structure()
    Solution.setup_database_structure()
    Theme.setup_database_structure()
