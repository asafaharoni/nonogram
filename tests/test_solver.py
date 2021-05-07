import pytest

from game.board.board import Board
from game.solver.analyze_the_guess_solver import AnalyzeThenGuessSolver


def test_analyee_then_guess_solver():
    a = Board.from_file(r'testdata\N.clean.png', True)
    AnalyzeThenGuessSolver(a).solve()
    assert a.is_board_solved()
    a = Board.from_file(r'testdata\N.dirty.png', True)
    AnalyzeThenGuessSolver(a).solve()
    assert a.is_board_solved()
    a = Board.from_instruction_file(r'testdata\1.ins')
    AnalyzeThenGuessSolver(a).solve()
    assert a.is_board_solved()
    a = Board.from_instruction_file(r'testdata\2.ins')
    AnalyzeThenGuessSolver(a).solve()
    assert a.is_board_solved()
    a = Board.from_instruction_file(r'testdata\3.ins')
    AnalyzeThenGuessSolver(a).solve()
    assert a.is_board_solved()
