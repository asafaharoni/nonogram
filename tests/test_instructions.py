from typing import List

from game.board.cell import CellRow, RowInstructions
from game.solver.solvertools.instructions import InstructionInfo, InstructionManager
from game.solver.solvertools.ranges import RangeInfo, RangesManager


def test_instruction_info__in_range():
    instruction = InstructionInfo(5, 10)
    assert instruction.in_range(RangeInfo(range(0, 10)))
    assert not instruction.in_range(RangeInfo(range(-1, 10)))
    assert not instruction.in_range(RangeInfo(range(0, 11)))
    instruction.set_min_start(3)
    assert instruction.in_range(RangeInfo(range(3, 10)))
    assert instruction.in_range(RangeInfo(range(3, 9)))
    assert not instruction.in_range(RangeInfo(range(2, 9)))
    assert not instruction.in_range(RangeInfo(range(3, 11)))
    instruction.set_max_stop(6)
    assert instruction.in_range(RangeInfo(range(3, 6)))
    assert instruction.in_range(RangeInfo(range(4, 5)))
    assert not instruction.in_range(RangeInfo(range(2, 6)))
    assert not instruction.in_range(RangeInfo(range(3, 7)))


def get_instruction_manager(bool_row: List[bool], instructions_as_int: List[int]) -> InstructionManager:
    row = CellRow.from_bool(bool_row)
    ranges_manager = RangesManager(row)
    instructions = RowInstructions.from_list(instructions_as_int)
    return InstructionManager(
        InstructionInfo.from_instructions(instructions, len(row)),
        ranges_manager)


def test_instruction_manager__different_ranges():
    bool_row: List[bool] = ([None] * 2 + [True] + [None] * 2 + [False] + [None] * 2 + [True] + [None] * 2)
    instructions = [2, 2]
    instruction_manager = get_instruction_manager(bool_row, instructions)
    ins_info = instruction_manager.get_instruction_info(0)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 1
    assert ins_info.get_max_stop() == 4
    ins_info = instruction_manager.get_instruction_info(1)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 7
    assert ins_info.get_max_stop() == 10


def test_instruction_manager__adjacent_blocks_not_in_same_range():
    bool_row: List[bool] = [None] * 6 + [True] + [False] + [True] + [None] * 2
    instructions = [3, 3]
    instruction_manager = get_instruction_manager(bool_row, instructions)
    ins_info = instruction_manager.get_instruction_info(0)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 4
    assert ins_info.get_max_stop() == 7
    ins_info = instruction_manager.get_instruction_info(1)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 8
    assert ins_info.get_max_stop() == 11


def test_instruction_manager__next_block_to_add_is_too_far():
    bool_row: List[bool] = [None] * 30
    bool_row[24] = True
    bool_row[8] = True
    bool_row[4] = True
    instructions = [13, 3]
    instruction_manager = get_instruction_manager(bool_row, instructions)
    ins_info = instruction_manager.get_instruction_info(0)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 0
    assert ins_info.get_max_stop() == 17
    ins_info = instruction_manager.get_instruction_info(1)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 22
    assert ins_info.get_max_stop() == 27


def test_instruction_manager__setup__successful_propagation_with_blocks():
    bool_row = [None, True, None, True, None]
    instructions = [2, 2]
    instruction_manager = get_instruction_manager(bool_row, instructions)
    ins_info = instruction_manager.get_instruction_info(0)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 0
    assert ins_info.get_max_stop() == 2
    ins_info = instruction_manager.get_instruction_info(1)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 3
    assert ins_info.get_max_stop() == 5


def test_instruction_manager__setup__successful_propagation_no_blocks():
    bool_row = [None] * 30
    instructions = [1] * 10
    instruction_manager = get_instruction_manager(bool_row, instructions)
    for i, instruction_info in enumerate(instruction_manager):
        # Test propagate right:
        assert instruction_info.get_min_start() == 2 * i
        assert instruction_info.get_min_stop() == 2 * i + 1
        # Test propagate left:
        assert instruction_info.get_max_start() == 2 * i + 11
        assert instruction_info.get_max_stop() == 2 * i + 12


def test_instruction_manager__setup__successful_propagation_last_instruction_no_blocks():
    bool_row = [None, True, None, True, None, None, None]
    instructions = [1] * 3
    instruction_manager = get_instruction_manager(bool_row, instructions)
    for i, instruction_info in enumerate(instruction_manager):
        # Test propagate right:
        assert instruction_info.get_min_start() == 2 * i + 1
        assert instruction_info.get_min_stop() == 2 * i + 2
    assert instruction_manager[0].has_blocks()
    assert instruction_manager[1].has_blocks()
    assert not instruction_manager[2].has_blocks()

    # Multiple last instructions
    bool_row = [None, True, None, True] + [None] * 10
    instructions = [1] * 5
    instruction_manager = get_instruction_manager(bool_row, instructions)
    for i, instruction_info in enumerate(instruction_manager):
        # Test propagate right:
        assert instruction_info.get_min_start() == 2 * i + 1
        assert instruction_info.get_min_stop() == 2 * i + 2
    assert instruction_manager[0].has_blocks()
    assert instruction_manager[1].has_blocks()
    for i in range(2, len(instructions)):
        assert not instruction_manager[i].has_blocks()


def test_instruction_manager__propagate_blocks_left__simple_cases():
    bool_row = [None] * 10 + [True] + [None] * 12
    instructions = [1] * 6
    im = get_instruction_manager(bool_row, instructions)
    for ins_index, instruction_info in enumerate(im):
        # Test propagate right:
        assert instruction_info.get_min_start() == 2 * ins_index
        assert instruction_info.get_max_start() == 2 * ins_index
        assert instruction_info.get_min_stop() == 2 * ins_index + 1
        assert instruction_info.get_max_stop() == 2 * ins_index + 1
        if ins_index == len(instructions) - 1:
            assert im[ins_index].has_blocks()
        else:
            assert not im[ins_index].has_blocks()

    # First back propagation.
    for instruction_with_block_index in range(4, 2, -1):
        im.propagate_blocks_left(im[instruction_with_block_index + 1])
        left = instruction_with_block_index
        right = len(instructions) - instruction_with_block_index - 1

        # Check all instructions left to the one containing the block.
        for ins_index in range(instruction_with_block_index):
            assert im[ins_index].get_min_start() == 2 * ins_index
            assert im[ins_index].get_min_stop() == 2 * ins_index + 1
            assert im[ins_index].get_max_start() == 10 + 2 * (ins_index - left)
            assert im[ins_index].get_max_stop() == 11 + 2 * (ins_index - left)
            assert not im[ins_index].has_blocks()

        # Check instruction with block.
        instruction_info = im[instruction_with_block_index]
        assert instruction_info.get_min_start() == 10
        assert instruction_info.get_min_stop() == 11
        assert instruction_info.get_max_start() == 10
        assert instruction_info.get_max_stop() == 11
        assert instruction_info.has_blocks()

        # Check all instructions right to the one containing the block.
        for loop_index, ins_index in enumerate(range(instruction_with_block_index + 1, len(instructions))):
            assert im[ins_index].get_min_start() == 12 + 2 * loop_index
            assert im[ins_index].get_min_stop() == 13 + 2 * loop_index
            assert im[ins_index].get_max_start() == 24 - 2 * (right - loop_index)
            assert im[ins_index].get_max_stop() == 25 - 2 * (right - loop_index)
            assert not im[ins_index].has_blocks()
