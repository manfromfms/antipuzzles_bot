"""
This module provides the same sqlite3.Connection for each caller. 

Module requirements:
None
"""

import sqlite3

from .src.database import db_init, get_connection

from pathlib import Path

def database_init(path: str | Path) -> sqlite3.Connection | None:
    """Generate db file or use existing one. Also sets up the db structure for all classes presented in this module.

    Args:
        path (str | Path): Path to a db file. (Local path is counted from the main python file)

    Returns:
        sqlite3.Connection: Connection to a db.
    """

    db_init(path)

    return get_connection()
