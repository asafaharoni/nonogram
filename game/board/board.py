from typing import List, Any

from game.board.cell import CellState, Location, Cell, CellRow, RowInstructions
from game.board.image_utils import image_to_array, array_to_image
from game.board.instructions_utils import instructions_from_file


class CellTable:
    def __init__(self, rows: int = None, columns=None, array: List[List[CellState]] = None):
        if rows:
            self.rows = rows
            if columns:
                self.columns = columns
            else:
                self.columns = rows
            self.table = [[Cell() for column in range(self.columns)] for row in range(self.rows)]
        elif array:
            self.rows = len(array)
            self.columns = len(array[0])
            self.table = [[Cell(state) for state in row] for row in array]

    @classmethod
    def from_image(cls, image_path: str):
        return CellTable(array=image_to_array(image_path))

    def to_image(self, image_path: str):
        array_to_image([[cell.state.value for cell in col] for col in self.table], image_path)

    def assert_location(self, location: Location):
        assert location.row in range(self.rows) and location.column in range(self.columns)

    def get_cell_state(self, location: Location):
        self.assert_location(location)
        return self.table[location.row][location.column].state

    def set_cell_state(self, location: Location, state: CellState):
        self.assert_location(location)
        self.table[location.row][location.column].set_state(state)

    def get_row(self, row: int):
        return CellRow(self.table[row])

    def get_column(self, column: int):
        return CellRow([self.table[row][column] for row in range(self.rows)])

    def __eq__(self, other):
        if self.rows != other.rows or self.columns != other.columns:
            return False
        for row, other_row in zip(self.table, other.table):
            for cell, other_cell in zip(row, other_row):
                if cell != other_cell:
                    return False
        return True

    def get_size(self):
        return self.rows, self.columns

    def get_steps(self):
        steps = 0
        for row in self.table:
            for cell in row:
                steps += cell.get_changes_num()
        return steps


def entry(text: Any = '', size: int = 3):
    template = '{:^' + str(size) + '}'
    return template.format(str(text))


class Board:
    def __init__(self,
                 row_instructions: List[RowInstructions],
                 column_instructions: List[RowInstructions],
                 solution_table: CellTable = None):
        self.game_table = CellTable(len(row_instructions), len(column_instructions))
        self.row_instructions = row_instructions
        self.column_instructions = column_instructions
        self.solution_table = solution_table
        self.steps = 0

    @classmethod
    def from_file(cls, image_path: str, with_solution: bool = False):
        solution_table = CellTable.from_image(image_path)
        row_instructions = []
        column_instructions = []
        for i in range(solution_table.rows):
            row_instructions.append(RowInstructions(solution_table.get_row(i)))
        for i in range(solution_table.columns):
            column_instructions.append(RowInstructions(solution_table.get_column(i)))
        if with_solution:
            return Board(row_instructions, column_instructions, solution_table)
        else:
            return Board(row_instructions, column_instructions)

    @classmethod
    def from_instruction_file(cls, file_path):
        row_instructions, column_instructions = instructions_from_file(file_path)
        return Board(row_instructions, column_instructions)

    def to_image(self, image_path: str):
        self.game_table.to_image(image_path)

    def print_solution(self):
        if self.solution_table:
            return self.print_table(self.solution_table)
        else:
            return "No solution\n" + self.print_game_table()

    def print_game_table(self):
        return self.print_table(self.game_table)

    def get_cell_state(self, location: Location):
        return self.game_table.get_cell_state(location)

    def set_cell_state(self, location: Location, state: CellState):
        self.steps = self.steps + 1
        return self.game_table.set_cell_state(location, state)

    def get_row(self, row: int):
        return self.game_table.get_row(row)

    def get_column(self, column: int):
        return self.game_table.get_column(column)

    @staticmethod
    def is_row_solved_(row: CellRow, instructions: RowInstructions):
        return RowInstructions.is_row_solved(row, instructions)

    def is_row_solved(self, row_num: int):
        return self.is_row_solved_(self.get_row(row_num), self.row_instructions[row_num])

    def is_column_solved(self, column_num: int):
        return self.is_row_solved_(self.get_column(column_num), self.column_instructions[column_num])

    def print_table(self, table: CellTable):
        rows = []
        indent = max(map(lambda x: len(x.instructions), self.row_instructions))
        top = max(map(lambda x: len(x.instructions), self.column_instructions))
        for row in range(top):
            row_entries = []
            for _ in range(indent):
                row_entries.append(entry())
            for ins in self.column_instructions:
                entry_index = len(ins) - top + row
                if entry_index < 0:
                    row_entries.append(entry())
                else:
                    row_entries.append(entry(ins[entry_index]))
            rows.append(''.join(row_entries))
        for row in range(table.rows):
            row_entries = []
            for j in range(indent):
                ins = self.row_instructions[row]
                entry_index = len(ins) - indent + j
                if entry_index < 0:
                    row_entries.append(entry())
                else:
                    row_entries.append(entry(ins[entry_index]))
            for cell in table.get_row(row):
                row_entries.append(entry(cell))
            rows.append(''.join(row_entries))
        return '\n'.join(rows)

    def get_size(self):
        return self.game_table.get_size()

    def is_board_solved(self):
        rows, columns = self.get_size()
        for row in range(rows):
            if not self.is_row_solved(row):
                return False
        for column in range(columns):
            if not self.is_column_solved(column):
                return False
        return True

    def get_row_instructions(self, row):
        return self.row_instructions[row]

    def get_column_instructions(self, column):
        return self.column_instructions[column]

    def get_steps(self):
        return self.game_table.get_steps()

    def is_there_mistake(self):
        if self.solution_table:
            for row, sol_row in zip(self.game_table.table, self.solution_table.table):
                for cell, sol_cell in zip(row, sol_row):
                    if cell.get_state() != CellState.UNSET and cell != sol_cell:
                        return True
        return False
