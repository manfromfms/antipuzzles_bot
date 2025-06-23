import sqlite3
from pathlib import Path

connection: sqlite3.Connection | None = None


def db_init(path: str | Path) -> sqlite3.Connection | None:
    """Initialise the database.

    Args:
        path (str | Path): Path to the database file. Local to the main directory.

    Returns:
        sqlite3.Connection | None: Connection to the database if required immediately.
    """

    global connection
    connection = sqlite3.connect(path)
    return connection


def get_connection() -> sqlite3.Connection | None:
    """Get current connection. Initialise the database first using db_init()

    Returns:
        sqlite3.Connection | None: Connection to the database.
    """
    global connection
    return connection
