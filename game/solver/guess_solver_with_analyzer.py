from game.board.board import Board
from game.board.cell import Location, CellState
from game.solver.guess_solver import GuessSolver
from game.solver.solver import Solver
from game.solver.solvertools.row_analyzer import RowAnalyzer
from game.solver.solvertools.guesslocator import BestInfoGuessLocator, ByOrderGuessLocator, Guess


class GuessSolverWithGuessLocator(GuessSolver):
    def __init__(self, board: Board):
        super().__init__(board)
        self.guess_locator = BestInfoGuessLocator(board)

    def next_guess_location(self, location: Location):
        return self.guess_locator.get_next_guess()

    def guess_(self, guess_location):
        self.guesses = self.guesses + 1
        if guess_location is None:
            if self.verbose:
                print(self.board.print_game_table())
            return self.board.is_board_solved()
        self.board.set_cell_state(guess_location, CellState.FILL)
        if self.verbose:
            print(self.board.print_game_table())
        if self.analyze_and_solve_(guess_location):
            return True
        self.board.set_cell_state(guess_location, CellState.NO_FILL)
        if self.verbose:
            print(self.board.print_game_table())
        if self.analyze_and_solve_(guess_location):
            return True
        self.board.set_cell_state(guess_location, CellState.UNSET)
        return False
