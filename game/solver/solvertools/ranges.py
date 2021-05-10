from typing import List, Optional

from game.board.cell import CellRow, CellState
from game.solver.solvertools.collections import ListNode, RangeDict, ListOfNodes


class RangeInfo:
    def __init__(self, rng: range):
        self.range = rng
        self.contains_blocks_ = False

    def mark_contains_blocks(self):
        self.contains_blocks_ = True

    def contains_blocks(self) -> bool:
        return self.contains_blocks_

    def get_start(self) -> int:
        return self.range.start

    def get_stop(self) -> int:
        return self.range.stop

    def __len__(self) -> int:
        return len(self.range)

    def __contains__(self, item) -> bool:
        if isinstance(item, int):
            return item in self.range
        if isinstance(item, range):
            return item[0] in self.range and item[-1] in self.range
        return False


class Block(ListNode, RangeInfo):
    def __init__(self, rng: range, containing_range: RangeInfo = None):
        super().__init__()
        super(ListNode, self).__init__(rng)
        self.containing_range = containing_range

    def get_containing_range(self):
        return self.containing_range

    def set_containing_range(self, containing_range: RangeInfo):
        containing_range.mark_contains_blocks()
        self.containing_range = containing_range


class BlockGroup(List[Block]):
    def add_(self, block: Block, index: int):
        if block is None:
            raise KeyError(f'No block to add to index {index}.')
        assert block.get_containing_range() == self.get_containing_range()
        self.insert(index, block)

    def left_add(self, block: Block) -> None:
        assert len(self) > 0 and block == self[0].get_prev()
        self.add_(self[0].get_prev(), 0)

    def right_add(self, block: Block) -> None:
        assert len(self) > 0 and block == self[-1].get_next()
        self.add_(self[-1].get_next(), -1)

    def remove_(self, index: int) -> Block:
        assert len(self) > 0
        block = self[index]
        del self[index]
        return block

    def left_remove(self) -> Block:
        return self.remove_(0)

    def right_remove(self) -> Block:
        return self.remove_(-1)

    def get_block_length(self) -> int:
        if len(self) == 0:
            return 0
        return self.get_stop() - self.get_start()

    def get_start(self) -> int:
        if len(self) == 0:
            return -1
        return self[0].get_start()

    def get_stop(self) -> int:
        if len(self) == 0:
            return -1
        return self[-1].get_stop()

    def get_containing_range(self) -> Optional[RangeInfo]:
        if len(self) == 0:
            return None
        return self[0].get_containing_range()


class RangesManager:
    def __init__(self, row: CellRow):
        self.row_length = len(row)
        self.ranges = RangeDict()
        self.blocks = ListOfNodes()
        start_idx = 0
        block_start_index = -1
        for i, cell in enumerate(row):
            if cell.get_state() == CellState.FILL:
                if block_start_index == -1:
                    block_start_index = i
            else:
                if cell.get_state() == CellState.NO_FILL:
                    if start_idx != i:
                        rng = range(start_idx, i)
                        self.ranges[rng] = RangeInfo(rng)
                    start_idx = i + 1
                if block_start_index > -1:
                    block_range = range(block_start_index, i)
                    self.blocks.append(Block(block_range))
                    block_start_index = -1
        if start_idx < len(row):
            rng = range(start_idx, len(row))
            self.ranges[rng] = RangeInfo(rng)
        self.next_called = False
        # set containing range for each Block:
        for block in self.blocks:
            assert isinstance(block, Block)
            block.set_containing_range(self.ranges[block.get_start()])

    def get_row_length(self):
        return self.row_length

    def get_ranges(self):
        return [self.ranges[key] for key in self.ranges.get_keys()]

    def get_blocks(self) -> ListOfNodes:
        return self.blocks

    def __contains__(self, item):
        return item in self.ranges

    def get_ranges_in_range(self, rng: RangeInfo) -> List[RangeInfo]:
        return [self.ranges[range_start] for range_start in self.ranges if self.ranges[range_start] in rng]
