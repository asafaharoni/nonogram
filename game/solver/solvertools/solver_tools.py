from typing import NamedTuple, List

from func_timeout import func_timeout, FunctionTimedOut

from game.board.board import Board, entry
from game.board.cell import CellRow, CellState, RowInstructions, Cell


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


class SingleInstruction(NamedTuple):
    value: int
    index: int


class RangeInfo:
    def __init__(self, rng: range):
        self.range = rng
        self.potential_instructions = []

    def add_instruction(self, instruction: SingleInstruction):
        self.potential_instructions.append(instruction)

    def is_there_potential(self):
        return len(self.potential_instructions) > 0

    def can_be_trimmed(self):
        return len(self.range) > 1

    def __getitem__(self, item):
        return self.range[item]

    def get_start_index(self):
        return self.range.start

    def get_stop_index(self):
        return self.range.stop

    def __contains__(self, item):
        if isinstance(item, int):
            return item in self.range
        if isinstance(item, range):
            return item[0] in self.range and item[-1] in self.range
        return False


class RangesManager:
    def __init__(self, row: CellRow):
        self.ranges = []
        start_idx = 0
        for i, cell in enumerate(row):
            if cell.to_bool() is False:
                if start_idx != i:
                    self.ranges.append(RangeInfo(range(start_idx, i)))
                start_idx = i + 1
        if start_idx < len(row):
            self.ranges.append(RangeInfo(range(start_idx, len(row))))
        self.next_called = False

    def __getitem__(self, item):
        return self.ranges[item]

    def __setitem__(self, key, value):
        self.ranges[key] = value

    def __len__(self):
        return len(self.ranges)

    def __contains__(self, item):
        for rng in self.ranges:
            if item in rng:
                return True
        return False

    def next(self):
        self.next_called = True
        if self.is_empty():
            return False
        if self[0].can_be_trimmed():
            self[0] = RangeInfo(self.ranges[0][1:])
        else:
            del self.ranges[0]
        return not self.is_empty()

    def is_empty(self):
        return len(self.ranges) == 0

    # TODO: move this logic somewhere else. Manager, not Solver.
    def simple_solution(self, instructions: RowInstructions):
        info_to_add = []
        instruction_iter = iter(instructions)
        countdown = next(instruction_iter)
        for index in self[0]:
            state = CellState.FILL
            if countdown == 0:
                state = CellState.NO_FILL
                countdown = next(instruction_iter)
            info_to_add.append(CellInfoToAdd(index, state))
        return info_to_add

    # TODO: move this logic somewhere else. Manager, not Solver.
    def attempt_solve(self, instructions: RowInstructions):
        if len(self) == 1 and len(self[0]) == instructions.get_min_length():
            return self.simple_solution(instructions)
        return []


class RowDisqualifier:
    pass


class RowAnalyzer:
    def __init__(self, row: CellRow, instructions: RowInstructions):
        self.row = row
        self.range_manager = RangesManager(row)
        self.instructions = instructions
        self.left_most_ranges = []
        self.is_solvable = self.can_solution_be_found_(0, self.instructions)

    def find_left_most_range_for_instruction(self, index: int, length: int):
        start_index = index
        for rng in self.range_manager:
            if rng.get_stop_index() <= index:
                continue
            start_index = max(start_index, rng.get_start_index())
            left_most_range = range(start_index, start_index + length)
            if left_most_range not in rng:
                if self.is_there_fill_in_range(left_most_range, rng):
                    return None
                continue
            while left_most_range.stop < len(self.row) and self.row[left_most_range.stop].get_state() == CellState.FILL:
                # Can the range be advanced by one?
                if self.row[left_most_range.start].get_state() == CellState.FILL:
                    # Range cannot be advanced, as it means the first filled cell is out of this range, which should be
                    # the left most range.
                    return None
                # Advance range by 1.
                left_most_range = self.get_next_range(left_most_range)
                # Is advanced range in row?
                if left_most_range not in rng:
                    return None
            return left_most_range
        return None

    def get_is_solvable(self):
        return self.is_solvable

    def get_left_most_ranges(self):
        if self.is_solvable:
            return self.left_most_ranges
        return None

    def reverse_range(self, rng: range):
        length = len(self.row)
        return range(length - rng.stop, length - rng.start)

    def get_right_most_ranges(self):
        if self.is_solvable:
            reversed_ranges = []
            for rng in self.left_most_ranges:
                reversed_ranges.append(self.reverse_range(rng))
            reversed_ranges.reverse()
            return reversed_ranges
        return None

    @staticmethod
    def get_next_range(rng: range):
        return range(rng.start + 1, rng.stop + 1)

    def can_solution_be_found_(self, location_index: int, instructions: RowInstructions):
        if instructions is None or len(instructions) == 0:
            return not self.is_there_fill_in_remainder(location_index)
        for start_index in range(location_index, len(self.row) - instructions[0] + 1):
            if start_index not in self.range_manager:
                continue
            left_most_range = self.find_left_most_range_for_instruction(start_index, instructions[0])
            if left_most_range is None:
                return False
            self.left_most_ranges.append(left_most_range)
            if self.can_solution_be_found_(left_most_range.stop + 1, instructions.get_next()):
                return True
            del self.left_most_ranges[-1]
            if self.row[left_most_range[0]].get_state() == CellState.FILL:
                return False
        return False

    def is_there_fill_in_range(self, left_most_range, rng: range):
        for index in left_most_range:
            if index == len(self.row) or index not in rng:
                return False
            if self.row[index].get_state() == CellState.FILL:
                return True
        return False

    def is_there_fill_in_remainder(self, start_index: int):
        for cell in self.row[start_index:]:
            if cell.get_state() == CellState.FILL:
                return True
        return False
