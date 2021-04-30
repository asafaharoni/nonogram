from enum import Enum
from typing import NamedTuple, List, Optional


class CellState(Enum):
    UNSET = None
    FILL = True
    NO_FILL = False

    def __str__(self):
        if self.value is None:
            return ' '
        elif self.value is False:
            return 'X'
        elif self.value is True:
            return u"\u2588\u2588"


class Location(NamedTuple):
    row: int
    column: int


class Cell:
    def __init__(self, state: CellState = CellState.UNSET):
        self.state = state
        self.changes = 0

    def get_state(self):
        return self.state

    def get_changes_num(self):
        return self.changes

    def set_state(self, state: CellState):
        self.changes = self.changes + 1
        self.state = state

    def to_bool(self):
        return self.state.value

    def __str__(self):
        return str(self.state)

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash((self.state, self.changes))

    @classmethod
    def from_bool(cls, state: bool):
        return Cell(CellState(state))


class CellRow:
    def __init__(self, cells: List[Cell]):
        self.cells = cells

    def __getitem__(self, key):
        return self.cells[key]

    def __setitem__(self, key, value):
        if key in range(len(self)):
            self.cells[key] = value

    def __len__(self):
        return len(self.cells)

    def set_state(self, index: int, state: CellState):
        self.cells[index].set_state(state)

    def is_fully_set(self):
        for cell in self.cells:
            if cell.state == CellState.UNSET:
                return False
        return True

    def get_cells(self):
        return self.cells

    @classmethod
    def from_bool(cls, row: List[Optional[bool]]):
        return CellRow(list(map(lambda x: Cell(CellState(x)), row)))

    def reverse(self):
        reversed_cells = self.cells.copy()
        reversed_cells.reverse()
        return CellRow(reversed_cells)


class RowInstructions:
    def __init__(self, row: CellRow):
        self.instructions = []
        fill_count = 0
        for cell in row:
            if cell.to_bool():
                fill_count += 1
            elif fill_count > 0:
                self.instructions.append(fill_count)
                fill_count = 0
        if fill_count > 0:
            self.instructions.append(fill_count)

    def get_instructions(self):
        return self.instructions

    def __getitem__(self, key):
        return self.instructions[key]

    def __len__(self):
        return len(self.instructions)

    def get_min_length(self):
        min_length = sum(self.instructions) + len(self.instructions) - 1
        return max(0, min_length)

    def __iter__(self):
        return iter(self.instructions)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for ins, other_ins in zip(self.instructions, other.instructions):
            if ins != other_ins:
                return False
        return True

    def get_next(self):
        if len(self) == 1:
            return None
        next_instructions = RowInstructions(CellRow([]))
        next_instructions.instructions = self.instructions[1:]
        return next_instructions

    @classmethod
    def from_list(cls, instructions: List[int]):
        row_instructions = RowInstructions(CellRow([]))
        for instruction in instructions:
            row_instructions.instructions.append(instruction)
        return row_instructions

    def reverse(self):
        reversed_instructions = self.instructions.copy()
        reversed_instructions.reverse()
        return self.from_list(reversed_instructions)

    @classmethod
    def is_row_solved(cls, row: CellRow, ins):
        return RowInstructions(row) == ins