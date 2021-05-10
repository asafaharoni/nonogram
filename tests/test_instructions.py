from game.board.cell import CellRow, RowInstructions, CellState
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


def test_instruction_manager__different_ranges():
    row = CellRow.from_bool([None] * 2 + [True] + [None] * 2 + [False] + [None] * 2 + [True] + [None] * 2)
    ranges_manager = RangesManager(row)
    instructions = RowInstructions.from_list([2, 2])
    instruction_manager = InstructionManager(
        InstructionInfo.from_instructions(instructions, len(row)),
        ranges_manager)
    ins_info = instruction_manager.get_instruction_info(0)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 1
    assert ins_info.get_max_stop() == 4
    ins_info = instruction_manager.get_instruction_info(1)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 7
    assert ins_info.get_max_stop() == 10


def test_instruction_manager__adjacent_blocks_not_in_same_range():
    row = CellRow.from_bool([None] * 6 + [True] + [False] + [True] + [None] * 2)
    ranges_manager = RangesManager(row)
    instructions = RowInstructions.from_list([3, 3])
    instruction_manager = InstructionManager(
        InstructionInfo.from_instructions(instructions, len(row)),
        ranges_manager)
    ins_info = instruction_manager.get_instruction_info(0)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 4
    assert ins_info.get_max_stop() == 7
    ins_info = instruction_manager.get_instruction_info(1)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 8
    assert ins_info.get_max_stop() == 11


def test_instruction_manager__next_block_to_add_is_too_far():
    row = CellRow.from_bool([None] * 30)
    row.set_state(24, CellState.FILL)
    row.set_state(4, CellState.FILL)
    row.set_state(8, CellState.FILL)
    ranges_manager = RangesManager(row)
    instructions = RowInstructions.from_list([13, 3])
    instruction_manager = InstructionManager(
        InstructionInfo.from_instructions(instructions, len(row)),
        ranges_manager)
    ins_info = instruction_manager.get_instruction_info(0)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 0
    assert ins_info.get_max_stop() == 17
    ins_info = instruction_manager.get_instruction_info(1)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 22
    assert ins_info.get_max_stop() == 27


def test_instruction_manager__setup__successful_propagation_with_blocks():
    row = CellRow.from_bool([None, True, None, True, None])
    ranges_manager = RangesManager(row)
    instructions = RowInstructions.from_list([2, 2])
    instruction_manager = InstructionManager(
        InstructionInfo.from_instructions(instructions, len(row)),
        ranges_manager)
    ins_info = instruction_manager.get_instruction_info(0)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 0
    assert ins_info.get_max_stop() == 2
    ins_info = instruction_manager.get_instruction_info(1)
    assert isinstance(ins_info, InstructionInfo)
    assert ins_info.get_min_start() == 3
    assert ins_info.get_max_stop() == 5


def test_instruction_manager__setup__successful_propagation_no_blocks():
    row = CellRow.from_bool([None] * 30)
    ranges_manager = RangesManager(row)
    instructions = RowInstructions.from_list([1] * 10)
    instruction_manager = InstructionManager(
        InstructionInfo.from_instructions(instructions, len(row)),
        ranges_manager)
    for i, instruction_info in enumerate(instruction_manager):
        assert instruction_info.get_min_start() == 2 * i
        assert instruction_info.get_min_stop() == 2 * i + 1
