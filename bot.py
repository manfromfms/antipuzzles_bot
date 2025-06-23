from source.modules.database import get_connection, init

init('./puzzles.db')

print(type(get_connection()))