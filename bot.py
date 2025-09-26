# First load telegram and database modules
import source.modules.telegram as tg
import source.modules.database as db

# Select database file
db.database_init('./puzzles.db')

# Init user data package
import source.modules.users_data
source.modules.users_data.users_data_init()

# Init daily challenges package
import source.modules.daily
source.modules.daily.daily_init()

# Import all commands
import source.modules.command_me
import source.modules.command_start
import source.modules.command_puzzle
import source.modules.command_top
import source.modules.command_hardest
import source.modules.command_help

# Init all commands
source.modules.command_me.command_me_init()
source.modules.command_start.command_start_init()
source.modules.command_puzzle.command_puzzle_init()
source.modules.command_top.command_top_init()
source.modules.command_hardest.command_hardest_init()
source.modules.command_help.command_help_init() # Help command should be the last one to init 

# Start telegram loop
tg.run_polling()