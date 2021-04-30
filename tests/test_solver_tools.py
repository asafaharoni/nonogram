import pytest

from game.board.cell import CellRow, RowInstructions, CellState, Cell, Location
from game.solver.solvertools.solver_tools import RowAnalyzer, RowInfoAdder, CellInfoToAdd

EMPTY_ROW = 'er'
FALSE_MIDDLE_ROW = 'fmr'
FALSE_MID_RIGHT_ROW = 'fmrr'
FALSE_MID_LEFT_ROW = 'fmlr'
SINGLE_ONE_INS = 'soi'
TRUE_RIGHT_ROW = 'trr'
TURE_RIGHT_FALSE_RIGHT_ROW = 'trfrr'
TURE_MID_FALSE_MID_LEFT_ROW = 'tmrfmlr'
FULL_ROW = 'fr'
TRUE_FALSE_ALT_ROW = 'trar'
MUTUAL_TRUE_ROW = 'mtr'
MUTUAL_TRUE_REVERSE_ROW = 'mtrr'
TWO_ONE_INS = '2oi'
THREE_ONE_INS = '3oi'
FOUR_ONE_INS = '4oi'
ONE_TWO_INS = '12'
TWO_THREE_INS = '23'
THREE_TWO_INS = '32'
FULL_INS = 'fi'
THREE_INS = 'ti'


@pytest.fixture
def data():
    return {
        EMPTY_ROW: CellRow.from_bool([None for i in range(5)]),
        FALSE_MIDDLE_ROW: CellRow.from_bool([None, None, False, None, None]),
        FALSE_MID_RIGHT_ROW: CellRow.from_bool([None, None, None, False, None]),
        FALSE_MID_LEFT_ROW: CellRow.from_bool([None, False, False, None, None]),
        TRUE_RIGHT_ROW: CellRow.from_bool([None, None, None, None, True]),
        TURE_RIGHT_FALSE_RIGHT_ROW: CellRow.from_bool([None, None, None, False, True]),
        FULL_ROW: CellRow.from_bool([True, True, True, True, True]),
        TRUE_FALSE_ALT_ROW: CellRow.from_bool([True, False, True, False, True]),
        TURE_MID_FALSE_MID_LEFT_ROW: CellRow.from_bool([None, False, True, None, None]),
        MUTUAL_TRUE_ROW: CellRow.from_bool(
            [None, None, None, None, None, None, True, False, None, None, None]),
        MUTUAL_TRUE_REVERSE_ROW: CellRow.from_bool(
            [None, None, None, False, True, None, None, None, None, None, None]),
        SINGLE_ONE_INS: RowInstructions.from_list([1]),
        TWO_ONE_INS: RowInstructions.from_list([1, 1]),
        THREE_ONE_INS: RowInstructions.from_list([1, 1, 1]),
        FOUR_ONE_INS: RowInstructions.from_list([1, 1, 1, 1]),
        ONE_TWO_INS: RowInstructions.from_list([1, 2]),
        TWO_THREE_INS: RowInstructions.from_list([2, 3]),
        THREE_TWO_INS: RowInstructions.from_list([3, 2]),
        FULL_INS: RowInstructions.from_list([5]),
        THREE_INS: RowInstructions.from_list([3]),
    }


def test_get_is_solvable__simple_rows(data):
    # Empty row:
    assert RowAnalyzer(data[EMPTY_ROW], data[SINGLE_ONE_INS]).get_is_solvable()
    assert RowAnalyzer(data[EMPTY_ROW], data[TWO_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[EMPTY_ROW], data[FOUR_ONE_INS]).get_is_solvable()
    assert RowAnalyzer(data[EMPTY_ROW], data[THREE_ONE_INS]).get_is_solvable()
    # No fill in middle row:
    assert RowAnalyzer(data[FALSE_MIDDLE_ROW], data[SINGLE_ONE_INS]).get_is_solvable()
    assert RowAnalyzer(data[FALSE_MIDDLE_ROW], data[TWO_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FALSE_MIDDLE_ROW], data[THREE_ONE_INS]).get_is_solvable()
    # No fill in mid right:
    assert RowAnalyzer(data[FALSE_MID_RIGHT_ROW], data[THREE_ONE_INS]).get_is_solvable()
    # No fill in [1,2]:
    assert RowAnalyzer(data[FALSE_MID_LEFT_ROW], data[TWO_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FALSE_MID_LEFT_ROW], data[THREE_ONE_INS]).get_is_solvable()
    # Instructions are [1, 2]:
    assert RowAnalyzer(data[EMPTY_ROW], data[ONE_TWO_INS]).get_is_solvable()
    assert RowAnalyzer(data[FALSE_MIDDLE_ROW], data[ONE_TWO_INS]).get_is_solvable()
    assert RowAnalyzer(data[FALSE_MID_LEFT_ROW], data[ONE_TWO_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FALSE_MID_RIGHT_ROW], data[ONE_TWO_INS]).get_is_solvable()
    # Rows with [UNSET, UNSET, UNSET, FALSE/UNSER, TRUE]:
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[THREE_ONE_INS]).get_is_solvable()
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[ONE_TWO_INS]).get_is_solvable()
    assert RowAnalyzer(data[TURE_RIGHT_FALSE_RIGHT_ROW], data[THREE_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[TURE_RIGHT_FALSE_RIGHT_ROW], data[ONE_TWO_INS]).get_is_solvable()


def test_get_is_solvalble__alternating(data):
    assert RowAnalyzer(data[TRUE_FALSE_ALT_ROW], data[THREE_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[TRUE_FALSE_ALT_ROW], data[TWO_ONE_INS]).get_left_most_ranges()
    assert not RowAnalyzer(data[TRUE_FALSE_ALT_ROW], data[SINGLE_ONE_INS]).get_left_most_ranges()


def test_get_is_solvable__full_row(data):
    assert RowAnalyzer(data[EMPTY_ROW], data[FULL_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FALSE_MIDDLE_ROW], data[FULL_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FALSE_MID_RIGHT_ROW], data[FULL_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FALSE_MID_LEFT_ROW], data[FULL_INS]).get_is_solvable()
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[FULL_INS]).get_is_solvable()
    assert not RowAnalyzer(data[TURE_RIGHT_FALSE_RIGHT_ROW], data[FULL_INS]).get_is_solvable()
    assert RowAnalyzer(data[FULL_ROW], data[FULL_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FULL_ROW], data[SINGLE_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FULL_ROW], data[TWO_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FULL_ROW], data[THREE_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FULL_ROW], data[FOUR_ONE_INS]).get_is_solvable()
    assert not RowAnalyzer(data[FULL_ROW], data[ONE_TWO_INS]).get_is_solvable()


def test_get_left_most_ranges__unset_row(data):
    assert RowAnalyzer(data[EMPTY_ROW], data[SINGLE_ONE_INS]).get_left_most_ranges() == \
           [range(0, 1)]
    assert RowAnalyzer(data[EMPTY_ROW], data[TWO_ONE_INS]).get_left_most_ranges() == \
           [range(0, 1), range(2, 3)]
    assert RowAnalyzer(data[EMPTY_ROW], data[THREE_ONE_INS]).get_left_most_ranges() == \
           [range(0, 1), range(2, 3), range(4, 5)]
    assert RowAnalyzer(data[EMPTY_ROW], data[ONE_TWO_INS]).get_left_most_ranges() == \
           [range(0, 1), range(2, 4)]


def test_get_left_most_ranges__middle_false_row(data):
    assert RowAnalyzer(data[FALSE_MIDDLE_ROW], data[SINGLE_ONE_INS]).get_left_most_ranges() == \
           [range(0, 1)]
    assert RowAnalyzer(data[FALSE_MIDDLE_ROW], data[TWO_ONE_INS]).get_left_most_ranges() == \
           [range(0, 1), range(3, 4)]
    assert RowAnalyzer(data[FALSE_MIDDLE_ROW], data[ONE_TWO_INS]).get_left_most_ranges() == \
           [range(0, 1), range(3, 5)]


def test_get_left_most_ranges__true_right_row(data):
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[SINGLE_ONE_INS]).get_left_most_ranges() == \
           [range(4, 5)]
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[TWO_ONE_INS]).get_left_most_ranges() == \
           [range(0, 1), range(4, 5)]
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[ONE_TWO_INS]).get_left_most_ranges() == \
           [range(0, 1), range(3, 5)]


def test_get_left_most_ranges__full_row(data):
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[SINGLE_ONE_INS]).get_left_most_ranges() == \
           [range(4, 5)]
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[TWO_ONE_INS]).get_left_most_ranges() == \
           [range(0, 1), range(4, 5)]
    assert RowAnalyzer(data[TRUE_RIGHT_ROW], data[ONE_TWO_INS]).get_left_most_ranges() == \
           [range(0, 1), range(3, 5)]


def test_get_left_most_ranges__no_fill_in_range__skip_to_next_range(data):
    assert RowAnalyzer(data[TURE_MID_FALSE_MID_LEFT_ROW], data[THREE_INS]).get_left_most_ranges() == [range(2, 5)]


def get_cell(state: CellState):
    return Cell(Location(0, 0), state)


def get_unset_cell():
    return get_cell(CellState.UNSET)


def get_no_fill_cell():
    return get_cell(CellState.NO_FILL)


def get_filled_cell():
    return get_cell(CellState.FILL)


# def test_row_analyzer_init__long_row(data):
#     ins = RowInstructions.from_list([1, 1, 1, 1, 1, 1, 2])
#     row = CellRow([get_unset_cell()] * 100 + [get_no_fill_cell(), get_filled_cell()])
#     assert RowAnalyzer(row, ins).get_is_solvable()

    # ins = RowInstructions.from_list([1, 1, 3, 3, 3, 7, 1])
    # row = CellRow([Cell(Location(0, 0))] * 73 + [Cell(Location(0, 0), CellState.FILL)] * 2 +
    #               [Cell(Location(0, 0), CellState.NO_FILL)] * 2)
    # assert RowAnalyzer(row, ins).get_is_solvable()


#
# def test_row_info_adder__existing_fill_in_adjacent_ranges_add_info(data):
#     info_to_add = RowInfoAdder(data[MUTUAL_TRUE_ROW], data[TWO_THREE_INS]).add_info()
#     assert len(info_to_add) == 1
#     assert info_to_add[0].state == CellState.FILL
#     info_to_add[0].set_cell()
#     assert data[MUTUAL_TRUE_ROW][5] == Cell(CellState.FILL)
#     info_to_add = RowInfoAdder(data[MUTUAL_TRUE_REVERSE_ROW], data[THREE_TWO_INS]).add_info()
#     assert len(info_to_add) == 1
#     assert info_to_add[0].state == CellState.FILL
#     info_to_add[0].set_cell()
#     assert data[MUTUAL_TRUE_ROW][5] == Cell(CellState.FILL)
#     info_to_add = RowInfoAdder(CellRow([Cell()] * 7), RowInstructions.from_list([2, 3])).add_info()
#     assert len(info_to_add) == 3
    #
    # info_to_add = RowInfoAdder(CellRow([Cell()] * 25), RowInstructions.from_list([2, 3, 16])).add_info()
    # assert len(info_to_add) == 15


