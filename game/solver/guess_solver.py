from game.board.board import Board
from game.board.cell import Location, CellState
from game.solver.solver import Solver
from game.solver.solvertools.guesslocator import Guess, ByOrderGuessLocator, MostInfoGuessLocator
from game.solver.solvertools.row_analyzer import RowAnalyzer


class GuessSolver(Solver):
    def __init__(self, board: Board, verbose: bool = False, wait_time: float = 0.0):
        super().__init__(board, verbose, wait_time)
        self.guess_locator = ByOrderGuessLocator(board)

    def next_guess_location(self, last_guess: Guess):
        if self.guess_locator:
            return self.guess_locator.get_next_guess(last_guess)
        return None

    def guess_(self, guess: Guess):
        self.add_guess_()
        if guess is None:
            if self.verbose:
                print(self.board.print_game_table())
            return self.board.is_board_solved()
        if self.attempt_guess_and_solve_(guess):
            return True
        if self.attempt_guess_and_solve_(guess.get_flipped_guess()):
            return True
        self.board.set_cell_state(guess.location, CellState.UNSET)
        return False

    def attempt_guess_and_solve_(self, guess: Guess):
        self.board.set_cell_state(guess.location, guess.state)
        if self.verbose:
            print(self.board.print_game_table())
        if self.analyze_and_solve_(guess):
            return True
        return False

    def analyze_and_solve_(self, guess: Guess):
        row_analyzer = RowAnalyzer(self.board.get_row(guess.location.row),
                                   self.board.get_row_instructions(guess.location.row))
        column_analyzer = RowAnalyzer(self.board.get_column(guess.location.column),
                                      self.board.get_column_instructions(guess.location.column))
        return row_analyzer.get_is_solvable() and column_analyzer.get_is_solvable() and self.solve_(
            self.next_guess_location(guess))

    def solve_(self, guess: Guess):
        return self.guess_(guess)

    def solve(self):
        self.start_count_time_()
        self.solve_(Guess(Location(0, 0), CellState.FILL))
        self.stop_count_time_()
        self.print_score_()


class BestInfoGuessSolver(GuessSolver):
    def __init__(self, board: Board):
        super().__init__(board)
        self.guess_locator = MostInfoGuessLocator(board)
