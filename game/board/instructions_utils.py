from game.board.cell import RowInstructions


def line_to_arr(line: str):
    return [int(item) for item in line.split()]


def instructions_from_file(file_path: str):
    row_instructions_as_int, column_instructions_as_int = [], []
    with open(file_path) as fh:
        do_row = True
        for i, line in enumerate(fh):
            if do_row:
                if 'COL' in line:
                    do_row = False
                    continue
                row_instructions_as_int.append(line_to_arr(line))
            else:
                column_instructions_as_int.append(line_to_arr(line))
    row_instructions = []
    column_instructions = []
    for row in row_instructions_as_int:
        row_instructions.append(RowInstructions.from_list(row))
    for column in column_instructions_as_int:
        column_instructions.append(RowInstructions.from_list(column))
    return row_instructions, column_instructions
