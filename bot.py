import source.modules.telegram as tg
import source.modules.database as db

db.database_init('./puzzles.db')

import source.modules.command_start
import source.modules.command_puzzle
import source.modules.command_help

source.modules.command_start.command_start_init()
source.modules.command_puzzle.command_puzzle_init()
source.modules.command_help.command_help_init()

tg.run_polling()