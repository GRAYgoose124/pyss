import pytest

from pyss.game.board.playable import Chessboard
from pyss.game.depthtree import MoveTree, Node

class TestSuite:
    def test_boardtree(self):
        board = Chessboard()
        board.initialize()

        tree = MoveTree(board)
