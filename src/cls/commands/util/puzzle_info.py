from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.cls.Puzzle import Puzzle

def complile_puzzle_info(puzzle: 'Puzzle'):
    game = puzzle.load_game()

    # TODO: сколько раз решена задача
    # TODO: оценка задачи
    s = f'Задача:\n\t{puzzle.id}\n' \
        +f'Рейтинг:\n\t{puzzle.elo}±{puzzle.elodev}\n'\
        +f'Решена:\n\tIn Progress раз\n'\
        +f'Оценка:\n\tIn Progress\n'\
        +f'Из партии:\n\t{game.Black} vs. {game.White}'

    return s