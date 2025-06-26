from source.modules.database import database_init
from source.modules.users import users_init, User

database_init('./puzzles.db')

print(User().searchById(939993565))