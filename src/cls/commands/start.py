from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ModuleLoader import ModuleLoader

import sqlite3
import telegram

async def start(ml: 'ModuleLoader', connection: sqlite3.Connection, message: telegram.Message):
    await message.reply_markdown('Бот с задачами по antichess.\n' \
        '[GitHub](https://github.com/manfromfms/antipuzzles_bot)\n\n' \
        'Список команд:\n\n' \
        '/puzzle /p\n' \
        '    Без аргументов - отобразить текущую позицию и информацию о текущей задаче\n' \
        '    id:[число] - информация о задаче\n\n' \
        '/me\n' \
        '    Без аргументов - информация о себе\n\n' \
        '/top\n' \
        '    Без аргументов - топ игроков\n\n' \
        '/preferences\n' \
        '    Без аргументов - редактировать настройки\n\n' \
        'Пример использования команд с параметрами:\n`/puzzle id:1238\n\n`' \
        'Иногда из-за нестабильности подключения бот может не отпрвить новую позицию, но засчитать ход. Один вариант решения этой проблемы - попросить текущую позицию через /puzzle.'
    )