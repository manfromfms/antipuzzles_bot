"""
This module contains user-related classes:
- User

Module requirements:
- database
"""

from .src.User import User

def users_init():
    User.setup_database_structure()
