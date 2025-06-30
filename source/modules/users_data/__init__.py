"""
This module expands class User:
- User_expanded

Module requirements:
- database
- users
"""

from .src.User import User_expand as User

from ..users import users_init

def users_data_init():
    users_init()

    User.setup_database_structure()
