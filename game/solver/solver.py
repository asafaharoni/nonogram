from abc import ABC, abstractmethod
from time import time, sleep

from game.board.board import Board
from game.solver.solvertools.guesslocator import Guess


class Solver(ABC):
    def __init__(self, board: Board, verbose: bool = False, wait_time: float = 0.0):
        self.board = board
        self.rows, self.columns = board.get_size()
        self.verbose = verbose
        self.wait_time = wait_time
        self.wait_cycle_start = 0.0
        self.start_time = None
        self.end_time = None
        self.duration_in_milli_seconds = None
        self.guesses = 0
        self.guess_locator = None

    @abstractmethod
    def solve(self):
        pass

    def add_guess_(self):
        self.guesses = self.guesses + 1

    def get_guesses(self):
        return self.guesses

    def start_count_time_(self):
        self.start_time = time()

    def stop_count_time_(self):
        self.duration_in_milli_seconds = (time() - self.start_time) * 1000

    def start_wait_cycle(self):
        while time() < self.wait_cycle_start + self.wait_time:
            sleep(0.05)
        self.wait_cycle_start = time()

    def print_score_(self):
        if self.board.is_board_solved():
            print(self.board.print_game_table())
            print('Good Job! The board was beat in {} steps, and {} guesses, in {:.2f} milli-seconds!'.format(
                self.board.get_steps(), self.guesses, self.duration_in_milli_seconds))
        else:
            print(self.board.print_game_table())
            print('Well... Something didn\'t work as planned...')



