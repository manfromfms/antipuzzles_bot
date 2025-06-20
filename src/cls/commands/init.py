from typing import TYPE_CHECKING

import telegram.ext
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telegram

# This function is supposed to make a new entry of a user in the database. The function must be silent.
async def init(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    user = ml.User.User(ml, connection, id=message.from_user.id, searchById=message.from_user.id)  # type: ignore
    preferences = ml.Preferences.Preferences(ml, connection, searchByUserId=user.id)

    if preferences.id == 0:
        preferences.create_entry(lang=message.from_user.language_code)

    user.nickname = message.from_user.full_name # type: ignore

    user.update_database_entry()