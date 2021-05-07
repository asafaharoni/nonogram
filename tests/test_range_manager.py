from typing import List

import pytest

from game.board.cell import CellState, Cell, CellRow
from game.solver.solvertools.solver_tools import RangesManager

UNSET_ROW = 'unset'
FULL_ROW = 'full'
FULL_TWO_PART_ROW = 'full2'
HALF_ROW = 'half'
SINGLE_FILL_ROW = 'single'
EMPTY_ROW = 'empty'
NO_IN_MIDDLE_ROW = 'middle'


@pytest.fixture
def test_tools():
    return {
        UNSET_ROW: CellRow([Cell() for i in range(5)]),
        EMPTY_ROW: CellRow([Cell(CellState.NO_FILL) for i in range(5)]),
        FULL_ROW: CellRow([Cell(CellState.FILL) for i in range(5)]),
        FULL_TWO_PART_ROW: CellRow.from_bool([
            True, True, True, False, True
        ]),
        HALF_ROW: CellRow.from_bool([
            True, True, True, False, False
        ]),
        SINGLE_FILL_ROW: CellRow.from_bool([
            False, False, True, False, False
        ]),
        NO_IN_MIDDLE_ROW: CellRow.from_bool([
            None, None, False, None, None
        ]),
    }
