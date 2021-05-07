import pytest

from game.board.board import Board
from game.board.cell import CellState, Location, Cell, CellRow, RowInstructions

BOARD = 'board'
ROWS = 'rows'
COLUMNS = 'columns'


@pytest.fixture
def supply_board_from_file():
    board = Board.from_file('testdata/N.dirty.png', True)
    return {
        BOARD: board,
        ROWS: len(board.get_column(0)),
        COLUMNS: len(board.get_row(0))
    }


def test_assert_location(supply_board_from_file):
    board = supply_board_from_file[BOARD]
    rows, columns = board.get_size()
    bad_location1 = Location(rows, columns)
    bad_location2 = Location(-1, -1)
    good_location = Location(0, 0)
    with pytest.raises(AssertionError):
        board.get_cell_state(bad_location1)
    with pytest.raises(AssertionError):
        board.set_cell_state(bad_location1, CellState.FILL)
    with pytest.raises(AssertionError):
        board.get_cell_state(bad_location2)
    with pytest.raises(AssertionError):
        board.set_cell_state(bad_location2, CellState.FILL)
    try:
        board.get_cell_state(good_location)
        board.set_cell_state(good_location, CellState.FILL)
    except AssertionError:
        raise pytest.fail('Good location was wrongly found out of bound.')


def test_get_set_cell_state(supply_board_from_file):
    board = supply_board_from_file[BOARD]
    rows, columns = board.get_size()
    location_to_change = Location(0, 0)

    for row in range(rows):
        for column in range(columns):
            assert board.get_cell_state(Location(row, column)) == CellState.UNSET

    board.set_cell_state(location_to_change, CellState.FILL)
    for row in range(rows):
        for column in range(columns):
            location = Location(row, column)
            if location == location_to_change:
                assert board.get_cell_state(location) == CellState.FILL
            else:
                assert board.get_cell_state(location) == CellState.UNSET

    board.set_cell_state(location_to_change, CellState.NO_FILL)
    for row in range(rows):
        for column in range(columns):
            location = Location(row, column)
            if location == location_to_change:
                assert board.get_cell_state(location) == CellState.NO_FILL
            else:
                assert board.get_cell_state(location) == CellState.UNSET

    board.set_cell_state(location_to_change, CellState.UNSET)
    for row in range(rows):
        for column in range(columns):
            assert board.get_cell_state(Location(row, column)) == CellState.UNSET


def cell_row_to_states(row: CellRow):
    return list(map(
        lambda x: x.state,
        row.get_cells()
    ))


def test_get_row_column(supply_board_from_file):
    board = supply_board_from_file[BOARD]
    rows, columns = board.get_size()

    assert cell_row_to_states(board.get_row(0)) == [
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET
    ]

    board.set_cell_state(Location(0, columns - 1), CellState.FILL)

    assert cell_row_to_states(board.get_row(0)) == [
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.FILL
    ]

    board.set_cell_state(Location(rows - 1, 0), CellState.NO_FILL)

    assert cell_row_to_states(board.get_column(0)) == [
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.NO_FILL
    ]

    board.set_cell_state(Location(0, 0), CellState.FILL)

    assert cell_row_to_states(board.get_row(0)) == [
        CellState.FILL,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.FILL
    ]
    assert cell_row_to_states(board.get_column(0)) == [
        CellState.FILL,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.UNSET,
        CellState.NO_FILL
    ]

def test_is_row_solved(supply_board_from_file):
    board = supply_board_from_file[BOARD]
    _, columns = board.get_size()
    assert not board.is_row_solved(0)
    for index in range(columns):
        board.set_cell_state(Location(0, index), CellState.NO_FILL)
        assert not board.is_row_solved(0)
    for index in [0, 1, 4, 6, 8]: # List of indexes where solution is filled.
        board.set_cell_state(Location(0, index), CellState.FILL)
        assert not board.is_row_solved(0)
    board.set_cell_state(Location(0, 9), CellState.FILL)
    assert board.is_row_solved(0)
    board.set_cell_state(Location(0, 0), CellState.UNSET)
    assert not board.is_row_solved(0)
    board.set_cell_state(Location(0, 0), CellState.NO_FILL)
    assert not board.is_row_solved(0)
