"""
This module contains preferences-related classes:
- Preferences

Module requirements:
- database
- users
"""

from .src.Preferences import Preferences

def preferences_init():
    Preferences.setup_database_structure()