import src.cls.Game as Game
import src.cls.Puzzle as Puzzle
import src.cls.Opening as Opening
import src.cls.Solution as Solution
import src.cls.Theme as Theme
import src.cls.User as User
import src.cls.Preferences as Preferences
import src.cls.PuzzleVote as PuzzleVote


class ModuleLoader:
    def __init__(self):
        self.Game = Game
        self.Puzzle = Puzzle
        self.Opening = Opening
        self.Solution = Solution
        self.Theme = Theme
        self.User = User
        self.Preferences = Preferences
        self.PuzzleVote = PuzzleVote
        