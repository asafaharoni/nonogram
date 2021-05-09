from collections import defaultdict

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
        self.blocks = BlockGroup()

    def get_length(self):
        return self.length

    def set_min_start(self, index):
        self.min_start = index

    def set_max_stop(self, index):
        self.max_stop = index

    def get_min_start(self):
        return self.min_start

    def get_max_stop(self):
        return self.max_stop

    def get_range(self):
        return range(self.min_start, self.max_stop)

    def get_block_group(self):
        return self.blocks

    def update_ranges(self) -> None:
        self.max_stop = min(self.blocks.get_start() + self.length, self.blocks[-1].get_containing_range().get_stop())
        if self.next:
            assert isinstance(self.next, InstructionInfo)
            # TODO: Raise error when self.next.min_start >= self.next.get_containing_range().stop
            self.next.min_start = max(self.next.min_start, self.min_start + self.length + 1)
        self.min_start = max(self.blocks.get_stop() - self.length, self.blocks[0].get_containing_range().get_start())
        if self.prev:
            assert isinstance(self.prev, InstructionInfo)
            # TODO: Raise error when self.prev.max_stop < self.prev.get_containing_range().start
            self.prev.max_stop = min(self.prev.max_stop, self.max_stop - self.length - 1)

    def add_left_block(self, block: Block):
        if len(self.blocks) == 0:
            self.blocks.append(block)
        else:
            self.blocks.left_add(block)
            if self.blocks.get_block_length() > self.get_length():
                self.blocks.left_remove()
                return False
        self.update_ranges()
        return True

    def in_range(self, range_info: RangeInfo) -> bool:
        return self.min_start <= range_info.get_start() and range_info.get_stop() <= self.max_stop

    def __eq__(self, other):
        return self.length == other.length and self.min_start == other.min_start and self.max_stop == other.max_stop

    def __hash__(self):
        return hash((self.length, self.min_start, self.max_stop))

    @classmethod
    def from_instructions(cls, instructions: RowInstructions, row_length: int) -> ListOfNodes:
        single_instruction_list = ListOfNodes()
        for instruction_length in instructions.get_instructions():
            instruction = InstructionInfo(instruction_length, row_length)
            single_instruction_list.append(instruction)
        return single_instruction_list


class InstructionManager:
    def __init__(self, instructions: ListOfNodes, range_manager: RangesManager):
        self.instructions = instructions
        self.range_manager = range_manager
        self.blocks = range_manager.get_blocks()
        self.instruction_to_blocks_map = defaultdict(BlockGroup)
        self.setup_instructions_to_block_map_()

    def setup_instructions_to_block_map_(self) -> InstructionInfo:
        if len(self.instructions) > 0 and len(self.blocks) > 0:
            ins = self.instructions[-1]
            assert isinstance(ins, InstructionInfo)
            for block in self.blocks.reverse():
                assert isinstance(block, Block)
                if not self.range_manager.are_indexes_in_same_range(block.get_start(),
                                                                    ins.get_block_group().get_start()) or \
                        not ins.add_left_block(block):
                    if ins.get_prev() is None:
                        return ins
                    ins = ins.get_prev()
                    if ins is None:
                        break
                    assert isinstance(ins, InstructionInfo)
                    ins.add_left_block(block)

    def get_instruction_info(self, instruction_index: int):
        return self.instructions[instruction_index]
