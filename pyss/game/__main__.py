from typing import Literal

from .board import Chessboard


class ChessGame:
    def __init__(self, board=None):
        self.board = board or Chessboard()
        self.turn: Literal["white", "black"] = "white"

    def make_move(self, move):
        pass