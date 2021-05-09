from typing import List

from game.board.cell import CellRow, CellState, RowInstructions
from game.solver.solvertools.instructions import InstructionInfo, InstructionManager
from game.solver.solvertools.ranges import RangeInfo, RangesManager


class RowAnalyzer:
    def __init__(self, row: CellRow, instructions: RowInstructions):
        self.row = row
        self.range_manager = RangesManager(row)
        self.instructions = InstructionInfo.from_instructions(instructions, len(row))
        self.instruction_manager = InstructionManager(self.instructions, self.range_manager)
        self.left_most_ranges = []
        self.is_solvable = self.can_solution_be_found_()

    def find_left_most_range_for_instruction(self, index: int, instruction: InstructionInfo):
        length = instruction.get_length()
        start_index = index
        for range_info in self.range_manager.get_ranges():
            if range_info.get_stop() <= index:
                continue
            start_index = max(start_index, range_info.get_start())
            left_most_range = range(start_index, start_index + length)
            if left_most_range not in range_info:
                if self.is_there_fill_in_range(left_most_range, range_info):
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
                if left_most_range not in range_info:
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

    def can_solution_be_found_(self) -> bool:
        return self.can_solution_be_found_with_mapping_(0, self.instructions.to_list())

    def can_solution_be_found_with_mapping_(self, location_index: int, instructions: List[InstructionInfo]) -> bool:
        if len(instructions) == 0:
            return not self.is_there_fill_in_remainder(location_index)
        for start_index in range(location_index, len(self.row) - instructions[0].length + 1):
            if start_index not in self.range_manager:
                continue
            left_most_range = self.find_left_most_range_for_instruction(start_index, instructions[0])
            if left_most_range is None:
                return False
            self.left_most_ranges.append(left_most_range)
            if self.can_solution_be_found_with_mapping_(left_most_range.stop + 1, instructions[1:]):
                return True
            del self.left_most_ranges[-1]
            if self.row[left_most_range[0]].get_state() == CellState.FILL:
                return False
        return False

    def is_there_fill_in_range(self, left_most_range, range_info: RangeInfo):
        for index in left_most_range:
            if index == len(self.row) or index not in range_info:
                return False
            if self.row[index].get_state() == CellState.FILL:
                return True
        return False

    def is_there_fill_in_remainder(self, start_index: int):
        for cell in self.row[start_index:]:
            if cell.get_state() == CellState.FILL:
                return True
        return False
