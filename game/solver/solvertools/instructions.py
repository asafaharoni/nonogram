from __future__ import annotations
from typing import List, Optional

from game.board.cell import RowInstructions
from game.solver.solvertools.collections import ListNode, ListOfNodes
from game.solver.solvertools.ranges import RangeInfo, RangesManager, BlockGroup, Block


class InstructionInfo(ListNode):
    def __init__(self, length: int, max_stop: int, min_start: int = 0):
        super().__init__()
        self.length = length
        self.min_start = min_start
        self.initial_min_start = min_start
        self.max_stop = max_stop
        self.initial_max_stop = max_stop
        self.blocks = BlockGroup()

    def get_length(self):
        return self.length

    def set_min_start(self, index):
        self.min_start = index

    def set_max_stop(self, index):
        self.max_stop = index

    def get_min_start(self):
        return self.min_start

    def get_max_start(self):
        return self.max_stop - self.length

    def get_max_stop(self):
        return self.max_stop

    def get_min_stop(self):
        return self.min_start + self.length

    def get_min_range(self):
        return range(self.min_start, self.get_min_stop())

    def has_blocks(self) -> bool:
        return len(self.blocks) > 0

    def propagate_range_left(self, include_other_blocks: bool, full_propagate: bool = False) -> None:
        initial_max_stop = self.max_stop
        self.max_stop = self.get_new_max_stop(include_other_blocks)
        if self.prev and (self.max_stop != initial_max_stop or full_propagate):
            self.prev.propagate_range_left(include_other_blocks=include_other_blocks)

    def get_new_max_stop(self, include_other_blocks: bool) -> int:
        max_stop_candidates = [candidate for candidate in [
            self.blocks.get_containing_range().get_stop() if len(self.blocks) > 0 else None,
            self.next.get_max_start() - 1 if self.next else None,
            self.blocks[-1].get_next().get_start() - 1 if (
                    include_other_blocks and len(self.blocks) and self.blocks[-1].get_next()) else None,
            self.blocks.get_start() + self.length if len(self.blocks) > 0 else None,
            self.initial_max_stop
        ] if candidate is not None]
        return min(max_stop_candidates)

    def propagate_range_right(self, include_other_blocks: bool, full_propagate: bool = False) -> None:
        initial_min_start = self.min_start
        self.min_start = self.get_new_min_start(include_other_blocks)
        if self.next and (self.min_start != initial_min_start or full_propagate):
            self.next.propagate_range_right(include_other_blocks=include_other_blocks)

    def get_new_min_start(self, include_other_blocks: bool) -> int:
        min_start_candidates = [candidate for candidate in [
            self.blocks.get_containing_range().get_start() if len(self.blocks) > 0 else None,
            self.prev.get_min_stop() + 1 if self.prev else None,
            self.blocks[0].get_prev().get_stop() + 1 if (
                    include_other_blocks and len(self.blocks) and self.blocks[0].get_prev()) else None,
            self.blocks.get_stop() - self.length if len(self.blocks) > 0 else None,
            self.initial_min_start
        ] if candidate is not None]
        return max(min_start_candidates)

    def propagate_blocks_left(self, blocks_to_add: List[Block] = ()) -> Optional[InstructionInfo]:
        blocks_to_remove = []
        if len(blocks_to_add) > 0:
            for block in blocks_to_add:
                # TODO: Optimize s.t. not every iteration requires so many propagations.
                while not self.add_right_block(block, False):
                    if len(self.blocks) > 0:
                        blocks_to_remove.append(self.blocks.left_remove())
                    else:
                        blocks_to_remove.append(block)
                        break
        else:
            if len(self.blocks) > 0:
                blocks_to_remove.append(self.blocks.left_remove())
            if self.get_new_max_stop(include_other_blocks=True) - \
                    self.get_new_min_start(include_other_blocks=True) < self.length:
                while len(self.blocks) > 0:
                    blocks_to_remove.append(self.blocks.left_remove())
        self.propagate_range_left(include_other_blocks=True)
        self.propagate_range_right(include_other_blocks=True)
        if len(blocks_to_remove) > 0:
            if self.prev:
                return self.prev.propagate_blocks_left(blocks_to_remove)
            # TODO: figure out how to handle blocks that are left out; None or error.
            return None
        return self

    def add_left_block(self, block: Block, include_other_blocks: bool) -> bool:
        if block.get_start() < self.min_start:
            return False
        else:
            if len(self.blocks) == 0:
                self.blocks.append(block)
            else:
                self.blocks.left_add(block)
        self.propagate_range_left(include_other_blocks=False)
        self.propagate_range_right(include_other_blocks=False)
        return True

    def add_right_block(self, block: Block, include_other_blocks: bool) -> bool:
        if self.max_stop < block.get_stop() or self.length < len(block):
            return False
        else:
            if len(self.blocks) == 0:
                self.blocks.append(block)
            else:
                self.blocks.right_add(block)
        self.propagate_range_right(include_other_blocks=include_other_blocks)
        self.propagate_range_left(include_other_blocks=include_other_blocks)
        return True

    def in_range(self, range_info: RangeInfo) -> bool:
        return self.min_start <= range_info.get_start() and range_info.get_stop() <= self.max_stop

    def __eq__(self, other):
        if other is None:
            return False
        return self.length == other.length and self.min_start == other.min_start and self.max_stop == other.max_stop

    def __hash__(self):
        return hash((self.length, self.min_start, self.max_stop))

    def get_containing_range(self):
        return self.blocks.get_containing_range()

    @classmethod
    def from_instructions(cls, instructions: RowInstructions, row_length: int) -> ListOfNodes:
        single_instruction_list = ListOfNodes()
        for instruction_length in instructions.get_instructions():
            instruction = InstructionInfo(instruction_length, row_length)
            single_instruction_list.append(instruction)
        if len(single_instruction_list):
            single_instruction_list[0].propagate_range_right(include_other_blocks=True, full_propagate=True)
            single_instruction_list[-1].propagate_range_left(include_other_blocks=True, full_propagate=True)
        return single_instruction_list


class InstructionManager:
    def __init__(self, instructions: ListOfNodes, range_manager: RangesManager):
        self.instructions = instructions
        self.range_manager = range_manager
        self.blocks = range_manager.get_blocks()
        self.setup_instructions_to_block_map_()

    def __getitem__(self, item) -> InstructionInfo:
        return self.instructions[item]

    def setup_instructions_to_block_map_(self) -> InstructionInfo:
        if len(self.instructions) > 0 and len(self.blocks) > 0:
            ins = self.instructions[-1]
            assert isinstance(ins, InstructionInfo)
            for block in self.blocks.reverse():
                assert isinstance(block, Block)
                while not ins.add_left_block(block, include_other_blocks=False):
                    if ins.get_prev() is None:
                        return ins
                    ins = ins.get_prev()
                    assert isinstance(ins, InstructionInfo)

    def get_instruction_info(self, instruction_index: int):
        return self.instructions[instruction_index]
