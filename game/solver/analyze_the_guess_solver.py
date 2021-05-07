from typing import List

from game.board.board import Board
from game.board.cell import CellState, Location, RowInstructions, CellRow
from game.solver.guess_solver import GuessSolver
from game.solver.solvertools.guesslocator import Guess, ByOrderGuessLocator, MostInfoGuessLocator
from game.solver.solvertools.info_adders import CellInfoToAdd, RowInfoAdder


class AnalyzeThenGuessSolver(GuessSolver):
    def __init__(self, board: Board, verbose: bool = False, wait_time: float = 0.0):
        super().__init__(board, verbose, wait_time)

    def is_row_solved_(self, row: int):
        return RowInstructions.is_row_solved(self.board.get_row(row), self.board.get_row_instructions(row))

    def is_column_solved_(self, column: int):
        return RowInstructions.is_row_solved(self.board.get_column(column), self.board.get_column_instructions(column))

    def get_row_info_(self, row: CellRow, instructions: RowInstructions):
        row_info = RowInfoAdder(row, instructions).add_info()
        if row_info:
            self.print_state()
            for info in row_info:
                info.set_cell()
        return row_info

    def add_row_info_(self, row: CellRow, instructions: RowInstructions, info_to_add: List[CellInfoToAdd]):
        if not row.is_fully_set():
            row_info = self.get_row_info_(row, instructions)
            if row_info:
                info_to_add.extend(row_info)
                return True
        return False

    def add_info(self):
        info_added = True
        info_to_add = []
        while not self.board.is_board_solved() and info_added:
            info_added = False
            for row in range(self.rows):
                if self.add_row_info_(self.board.get_row(row), self.board.get_row_instructions(row), info_to_add):
                    info_added = True
            for column in range(self.columns):
                if self.add_row_info_(self.board.get_column(column), self.board.get_column_instructions(column),
                                      info_to_add):
                    info_added = True
        return info_to_add

    def print_state(self, guess: Guess = None):
        if self.verbose:
            self.start_wait_cycle()
            print(self.board.print_game_table(), flush=True)
            if guess:
                print(f'Guessed: {guess.location}', flush=True)

    def solve_(self, guess: Guess = Guess(Location(-1, -1), CellState.FILL)):
        added_info = self.add_info()
        if self.board.is_board_solved():
            return True
        if self.guess_(self.next_guess_location(guess)):
            return True
        if guess.location != Location(-1, -1):
            for info in added_info:
                info.unset_cell()
        return False

    def solve(self):
        self.start_count_time_()
        self.solve_()
        self.stop_count_time_()
        self.print_score_()


class AnalyzeSkipUnchangedInfoGuessSolver(AnalyzeThenGuessSolver):
    def add_info(self):
        info_to_add = []
        rows_to_check = list(range(self.rows))
        columns_to_check = list(range(self.columns))
        while not self.board.is_board_solved() and (rows_to_check or columns_to_check):
            rows_to_check = []
            columns_to_check = []
            for row in range(self.rows):
                info = (self.get_row_info_(self.board.get_row(row), self.board.get_row_instructions(row)))
                if info:
                    info_to_add.extend(info)
                    columns_to_check.extend([cell_info.cell.get_location().column for cell_info in info])
            for column in range(self.columns):
                info = self.get_row_info_(self.board.get_column(column), self.board.get_column_instructions(column))
                if info:
                    info_to_add.extend(info)
                    rows_to_check.extend([cell_info.cell.get_location().row for cell_info in info])
        return info_to_add


class AnalyzeThenBestInfoGuessSolver(AnalyzeThenGuessSolver):
    def __init__(self, board: Board):
        super().__init__(board)
        self.guess_locator = MostInfoGuessLocator(board)
