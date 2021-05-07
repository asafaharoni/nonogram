from abc import ABC, abstractmethod
from typing import NamedTuple

from game.board.board import Board
from game.board.cell import Location, CellState
from game.solver.solvertools.info_adders import BoardInfoAdder


class Guess(NamedTuple):
    location: Location
    state: CellState

    def get_flipped_guess(self):
        flipped_state = CellState.FILL
        if self.state == CellState.FILL:
            flipped_state = CellState.NO_FILL
        return Guess(self.location, flipped_state)


class GuessLocator(ABC):
    def __init__(self, board: Board):
        self.board = board
        self.rows, self.columns = board.get_size()

    @abstractmethod
    def get_next_guess(self, last_guess: Guess):
        pass


class ByOrderGuessLocator(GuessLocator):
    def __init__(self, board: Board):
        super().__init__(board)

    def get_next_guess(self, last_guess: Guess):
        next_location = last_guess.location
        if last_guess.location == Location(-1, -1):
            next_location = Location(0, 0)
        while next_location == last_guess.location or self.board.get_cell_state(next_location) != CellState.UNSET:
            if next_location.column == self.columns - 1:
                if next_location.row == self.rows - 1:
                    return None
                next_location = Location(next_location.row + 1, 0)
            else:
                next_location = Location(next_location.row, next_location.column + 1)
        return Guess(next_location, CellState.FILL)


class MostInfoGuessLocator(GuessLocator):
    def __init__(self, board: Board):
        super().__init__(board)
        self.info_adder = BoardInfoAdder(self.board)

    def get_next_guess(self, last_guess: Guess):
        best_guess = None
        best_info_added_count = -1
        for row_num, row in enumerate(self.board.game_table.table):
            for col_num, cell in enumerate(row):
                if cell.get_state() == CellState.UNSET:
                    for state in [CellState.FILL, CellState.NO_FILL]:
                        cell.set_state(state)
                        info_added = self.info_adder.add_info()
                        if len(info_added) > best_info_added_count:
                            best_guess = Guess(Location(row_num, col_num), state)
                            best_info_added_count = len(info_added)
                        for cell in info_added:
                            cell.set_state(CellState.UNSET)
                    cell.set_state(CellState.UNSET)
        return best_guess
