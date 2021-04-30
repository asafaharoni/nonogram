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


def test_is_empty(test_tools):
    manager = RangesManager(test_tools[UNSET_ROW])
    assert not manager.is_empty()
    manager = RangesManager(test_tools[FULL_ROW])
    assert not manager.is_empty()
    manager = RangesManager(test_tools[EMPTY_ROW])
    assert manager.is_empty()
    manager = RangesManager(CellRow([]))
    assert manager.is_empty()


def test_next(test_tools):
    manager = RangesManager(test_tools[UNSET_ROW])
    for i in range(4):
        assert len(manager.ranges) == 1
        assert manager.ranges[0].range == range(i, 5)
        assert manager.next()
    assert len(manager.ranges) == 1
    assert manager.ranges[0].range == range(4, 5)
    assert manager.next() is False
    assert manager.is_empty()

    manager = RangesManager(test_tools[FULL_ROW])
    for i in range(4):
        assert len(manager.ranges) == 1
        assert manager.ranges[0].range == range(i, 5)
        assert manager.next()
    assert len(manager.ranges) == 1
    assert manager.ranges[0].range == range(4, 5)
    assert manager.next() is False
    assert manager.is_empty()

    manager = RangesManager(test_tools[FULL_TWO_PART_ROW])
    for i in range(3):
        assert len(manager.ranges) == 2
        assert manager.ranges[0].range == range(i, 3)
        assert manager.ranges[1].range == range(4, 5)
        assert manager.next()
    assert len(manager.ranges) == 1
    assert manager.ranges[0].range == range(4, 5)
    assert manager.next() is False
    assert manager.is_empty()

    manager = RangesManager(test_tools[NO_IN_MIDDLE_ROW])
    for i in range(2):
        assert len(manager.ranges) == 2
        assert manager.ranges[0].range == range(i, 2)
        assert manager.ranges[1].range == range(3, 5)
        assert manager.next()
    assert len(manager.ranges) == 1
    assert manager.ranges[0].range == range(3, 5)
    assert manager.next()
    assert len(manager.ranges) == 1
    assert manager.ranges[0].range == range(4, 5)
    assert manager.next() is False
    assert manager.is_empty()


def test_attempt_solve(test_tools):
    assert True
