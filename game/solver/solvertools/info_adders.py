from typing import NamedTuple, List

from game.board.board import Board, entry
from game.board.cell import Cell, CellState, CellRow, RowInstructions
from game.solver.solvertools.solver_tools import RowAnalyzer


class CellInfoToAdd(NamedTuple):
    cell: Cell
    state: CellState

    def set_cell(self):
        if self.cell.get_state() != self.state:
            self.cell.set_state(self.state)

    def unset_cell(self):
        self.cell.set_state(CellState.UNSET)


class BoardInfoAdder:
    def __init__(self, board: Board):
        self.board = board
        self.rows, self.columns = board.get_size()

    @staticmethod
    def add_row_info_(row: CellRow, instructions: RowInstructions):
        if row.is_fully_set():
            return []
        return RowInfoAdder(row, instructions).add_info()

    def add_info(self):
        info_added = True
        info_to_add = []
        while not self.board.is_board_solved() and info_added:
            info_added = False
            for row in range(self.rows):
                info = self.add_row_info_(self.board.get_row(row), self.board.get_row_instructions(row))
                if info:
                    info_to_add.extend(info)
                    info_added = True
            for column in range(self.columns):
                info = self.add_row_info_(self.board.get_column(column), self.board.get_column_instructions(column))
                if info:
                    info_to_add.extend(info)
                    info_added = True
        return info_to_add


class RowInfoAdder:
    def __init__(self, row: CellRow, instructions: RowInstructions):
        self.left_most_ranges = RowAnalyzer(row, instructions).get_left_most_ranges()
        self.right_most_ranges = RowAnalyzer(row.reverse(), instructions.reverse()).get_right_most_ranges()
        self.row = row
        self.instructions = instructions

    def add_info(self):
        if self.left_most_ranges is None or self.right_most_ranges is None:
            return False
        info_added = []
        # Find cells that are in both ranges of an instructions, and fill them.
        for left_rng, right_rng in zip(self.left_most_ranges, self.right_most_ranges):
            info_added.extend(self.add_fill_info_(left_rng, right_rng))
        # Find cells that are in both ranges of adjacent instructions, and fill them.
        for left_rng, right_rng in zip(self.left_most_ranges[1:], self.right_most_ranges[:-1]):
            if self.are_mutual_ranges_blocked(left_rng, right_rng):
                info_added.extend(self.add_fill_info_(left_rng, right_rng))
        # Find cells that cannot be filled, and mark as no fill.
        for left_rng, right_rng in zip(
            self.left_most_ranges + [range(len(self.row), -1)],
            [range(-1, 0)] + self.right_most_ranges
        ):
            info_added.extend(self.add_no_fill_info_(left_rng, right_rng))
        return info_added

    def add_no_fill_info_(self, left_rng, right_rng):
        info_added = []
        for index in range(right_rng.stop, left_rng.start):
            assert self.row[index].get_state() != CellState.FILL
            if self.row[index].get_state() != CellState.NO_FILL:
                info_added.append(CellInfoToAdd(self.row[index], CellState.NO_FILL))
        return info_added

    def add_fill_info_(self, left_rng, right_rng):
        info_added = []
        indexes_to_fill_set = set(left_rng).intersection(set(right_rng))
        for index in indexes_to_fill_set:
            assert self.row[index].get_state() != CellState.NO_FILL
            if self.row[index].get_state() == CellState.UNSET:
                info_added.append(CellInfoToAdd(self.row[index], CellState.FILL))
        return info_added

    def print(self):
        text = 'Ranges [left, marked, right]:\n'
        text += self.print_row(self.ranges_to_cell_row(self.left_most_ranges)) + '\n'
        text += self.print_row(self.row) + '\n'
        text += self.print_row(self.ranges_to_cell_row(self.right_most_ranges))
        print(text, flush=True)

    def ranges_to_cell_row(self, ranges: List[range]):
        row = CellRow([Cell()] * len(self.row))
        for rng in ranges:
            for index in rng:
                row.cells[index] = Cell(CellState.FILL)
        return row

    @staticmethod
    def print_row(row: CellRow):
        row_text = ''
        for cell in row:
            row_text += entry(str(cell))
        return row_text

    def are_mutual_ranges_blocked(self, left_rng: range, right_rng: range):
        return (right_rng.stop < len(self.row) and
                self.row[right_rng.stop].get_state() == CellState.NO_FILL and
                self.row[right_rng.stop - 1].get_state() == CellState.FILL) or \
                (left_rng.start > 0 and
                 self.row[left_rng.start - 1].get_state() == CellState.NO_FILL and
                 self.row[left_rng.start].get_state() == CellState.FILL)