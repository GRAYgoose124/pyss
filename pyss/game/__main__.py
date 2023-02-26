from typing import Literal

from .board import Chessboard


class ChessGame:
    def __init__(self, board=None):
        self.board = board or Chessboard()
        self.turn: Literal["white", "black"] = "white"

    def move(self, position, new_position):
        if self.turn != self.board.get_piece_at(position).color:
            return False
        
        self.board.move(position, new_position)
        self.turn = "black" if self.turn == "white" else "white"

    