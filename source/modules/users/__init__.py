"""
This module contains puzzle classes:
- User

Module requirements:
- database
"""

from .src.User import User

def puzzles_init():
    User.setup_database_structure()
