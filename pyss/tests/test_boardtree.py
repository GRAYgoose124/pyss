import pytest

from pyss.game.board.depth import Chessboard


class TestSuite:
    def test_boardtree(self):
        board = Chessboard()
        board.initialize()

        tree = board.valid_move_tree()

        print(tree)
