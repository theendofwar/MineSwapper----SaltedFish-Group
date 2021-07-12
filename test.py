

import numpy as np
from collections import OrderedDict, deque, defaultdict
from traceback import print_exc
import itertools as it
import random

class Minefield:
    """
    Class to let the AI keep track of game world state.
    """

    # 0-8: mine proximity
    # -1: unknown, unflagged
    # -2: unknown, flagged
    TILE_VALUES = frozenset(range(-2, 9))
    UNFLAGGED = -1
    FLAGGED = -2

    def __init__(self, dim_x, dim_y, start_x, start_y, total_mines):
        # Create an empty starting minefield
        self.board = np.full((dim_x, dim_y), self.UNFLAGGED, dtype=np.int8)

        self.total_mines = total_mines

    def __getitem__(self, key):
        # direct pass through to underlying ndarray
        return self.board[key]

    def __setitem__(self, key, value):
        self.board[key] = value

    @property
    def dim_x(self):
        return self.board.shape[0]

    @property
    def dim_y(self):
        return self.board.shape[1]

    def check_in_bounds(self, x, y):
        return (0 <= x < self.dim_x) and (0 <= y < self.dim_y)

    def get_report(self):
        return defaultdict(int, zip(*np.unique(self.board, return_counts=True)))


a = Minefield(5,5,1,1,1)
print(a.get_report())
