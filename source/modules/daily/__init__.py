"""
This module contains daily-challenge related classes.


Module requirements:
- database
"""

from .src.Daily import Daily

def daily_init():
    Daily.setup_database_structure()