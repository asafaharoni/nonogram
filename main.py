from game.board.board import Board
from game.solver.guess_solver import GuessSolver, BestInfoGuessSolver
# from game.solver.guess_solver_with_analyzer import GuessSolverWithAnalyzer, GuessSolverWithGuessLocator
from game.solver.analyze_the_guess_solver import AnalyzeThenGuessSolver, AnalyzeThenBestInfoGuessSolver, \
    AnalyzeSkipUnchangedInfoGuessSolver

if __name__ == '__main__':
    # a = Board.from_file("data\\images\\N2.png", True)
    # GuessSolver(a).solve()
    # a = Board.from_instruction_file("data\\instructions\\1.ins")
    # a = Board.from_instruction_file("data\\instructions\\3.ins")
    # a = Board.from_file("data\\images\\N3.png")
    # a = Board.from_file("data\\images\\1.png", True)
    # a.to_image(r'data\images\1.png')
    # a = Board.from_file("data\\images\\maayan.squar.png", True)
    a = Board.from_file("data\\images\\maayan.bw.small.png")
    # AnalyzeThenGuessSolver(a, True, 0.3).solve()
    AnalyzeThenGuessSolver(a, True).solve()
    # AnalyzeThenGuessSolver(a).solve()
    # a = Board.from_file("data\\images\\1.png", True)
    # a = Board.from_file("data\\images\\maayan.squar.png", True)
    # AnalyzeSkipUnchangedInfoGuessSolver(a, True).solve()
    # AnalyzeSkipUnchangedInfoGuessSolver(a).solve()
    # a = Board.from_instruction_file("data\\instructions\\3.ins")
    # a = Board.from_instruction_file("data\\instructions\\1.ins")
    # AnalyzeThenBestInfoGuessSolver(a).solve()
    # a = Board.from_instruction_file("data\\instructions\\3.ins")
    # a = Board.from_file("data\\images\\N3.png")
    # GuessSolver(a, True).solve()
    # GuessSolver(a).solve()
    # a = Board.from_instruction_file("data\\instructions\\1.ins")
    # a = Board.from_file("data\\images\\N3.png")
    # BestInfoGuessSolver(a).solve()
    # GuessSolverWithGuessLocator(a).solve()
