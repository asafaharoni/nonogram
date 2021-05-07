from typing import List

from game.board.cell import CellRow, CellState, RowInstructions
from game.solver.solvertools.collections import RangeDict, ListNode


class InstructionInfo(ListNode):
    def __init__(self, length: int, left_most_index: int = 0):
        super().__init__()
        self.length = length
        self.left_most_index = left_most_index

    def get_length(self):
        return self.length

    def get_left_most_index(self):
        return self.left_most_index

    def __eq__(self, other):
        return self.length == other.length and self.left_most_index == other.left_most_index

    @classmethod
    def from_instructions(cls, instructions: RowInstructions):
        last_instruction = None
        single_instruction_list = []
        for instruction_length in instructions.get_instructions():
            instruction = InstructionInfo(instruction_length)
            if last_instruction:
                last_instruction.set_next(instruction)
            single_instruction_list.append(instruction)
            last_instruction = instruction
        return single_instruction_list


class Block(ListNode):
    def __init__(self, rng: range):
        super().__init__()
        self.range = rng


class RangeInfo:
    def __init__(self, rng: range, blocks: List[Block]):
        self.range = rng
        self.blocks = blocks

    def contains_blocks(self):
        return len(self.blocks) > 0

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
        self.ranges = RangeDict()
        self.blocks = RangeDict()
        start_idx = 0
        block_start_index = -1
        self.left_most_block = None
        last_block = None
        range_blocks = []
        for i, cell in enumerate(row):
            if cell.get_state() == CellState.FILL:
                if block_start_index == -1:
                    block_start_index = i
            else:
                if cell.get_state() == CellState.NO_FILL:
                    if start_idx != i:
                        rng = range(start_idx, i)
                        self.ranges[rng] = RangeInfo(rng, range_blocks)
                        range_blocks = []
                    start_idx = i + 1
                if block_start_index > -1:
                    block_range = range(block_start_index, i)
                    current_block = Block(block_range)
                    self.blocks[block_range] = current_block
                    range_blocks.append(current_block)
                    if self.left_most_block is None:
                        self.left_most_block = current_block
                    if last_block:
                        last_block.set_next(current_block)
                    last_block = current_block
                    block_start_index = -1
        if start_idx < len(row):
            rng = range(start_idx, len(row))
            self.ranges[rng] = RangeInfo(rng, range_blocks)
        self.next_called = False

    def get_ranges(self):
        return [self.ranges[key] for key in self.ranges.get_keys()]

    def __contains__(self, item):
        return item in self.ranges

    def are_indexes_in_same_range(self, index1: int, index2: int):
        return self.ranges[index1] == self.ranges[index2]


class RowAnalyzer:
    def __init__(self, row: CellRow, instructions: RowInstructions):
        self.row = row
        self.range_manager = RangesManager(row)
        self.left_most_ranges = []
        self.is_solvable = self.can_solution_be_found_(
            0, InstructionInfo.from_instructions(instructions))

    def find_left_most_range_for_instruction(self, index: int, instruction: InstructionInfo):
        length = instruction.get_length()
        start_index = index
        for range_info in self.range_manager.get_ranges():
            if range_info.get_stop_index() <= index:
                continue
            start_index = max(start_index, range_info.get_start_index())
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

    def can_solution_be_found_(self, location_index: int, instructions: List[InstructionInfo]):
        if len(instructions) == 0:
            return not self.is_there_fill_in_remainder(location_index)
        for start_index in range(location_index, len(self.row) - instructions[0].length + 1):
            if start_index not in self.range_manager:
                continue
            left_most_range = self.find_left_most_range_for_instruction(start_index, instructions[0])
            if left_most_range is None:
                return False
            self.left_most_ranges.append(left_most_range)
            if self.can_solution_be_found_(left_most_range.stop + 1, instructions[1:]):
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
