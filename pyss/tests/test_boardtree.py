import pytest

from pyss.game.board.playable import PlayableBoard
from pyss.game.depthtree import MoveTree, DepthNode


class TestSuite:
    def test_boardtree(self):
        board = PlayableBoard()
        board.initialize()

        tree = MoveTree(board)
