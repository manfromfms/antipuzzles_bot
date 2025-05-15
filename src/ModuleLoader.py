import src.cls.Game as Game
import src.cls.Puzzle as Puzzle
import src.cls.Opening as Opening
import src.cls.Solution as Solution
import src.cls.Category as Category
import src.cls.User as User

class ModuleLoader:
    def __init__(self):
        self.Game = Game
        self.Puzzle = Puzzle
        self.Opening = Opening
        self.Solution = Solution
        self.Category = Category
        self.User = User