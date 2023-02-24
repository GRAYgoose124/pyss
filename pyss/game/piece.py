import logging

from dataclasses import dataclass, field
from random import choice
from typing import Literal


logger = logging.getLogger(__name__)


# piece_dict[piece_type] contains the notation and both unicode characters for each piece
piece_dict = {
    "pawn": {
        "notation": "",
        "unicode": {
            "white": "♙",
            "black": "♟"
        },
        "initial_positions": {
            "white": [(6, i) for i in range(8)],
            "black": [(1, i) for i in range(8)]
        },
        "valid_relative_moves": {
            "white": [(1, 0)],
            "black": [(-1, 0)]
        },
        "valid_relative_captures": {
            "white": [(1, 1), (1, -1)],
            "black": [(-1, 1), (-1, -1)]
        },
        "displacement": 1,
        "value": 1
    },
    "rook": {
        "notation": "R",
        "unicode": {    
            "white": "♖",
            "black": "♜"
        },
        "initial_positions": {
            "white": [(7, 0), (7, 7)],
            "black": [(0, 0), (0, 7)]
        },
        "valid_relative_moves": {
            "white": [(0, 1), (0, -1), (1, 0), (-1, 0)],
            "black": True
        },
        "valid_relative_captures": True,
        "displacement": 7,
        "value": 5
    },
    "knight": {
        "notation": "N",
        "unicode": {
            "white": "♘",
            "black": "♞"
        },
        "initial_positions": {
            "white": [(7, 1), (7, 6)],
            "black": [(0, 1), (0, 6)]
        },
        "valid_relative_moves": {
            "white": [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
            "black": True
        },
        "valid_relative_captures": True,
        "displacement": 1,
        "value": 3
    },
    "bishop": {
        "notation": "B",
        "unicode": {
            "white": "♗",
            "black": "♝"
        },
        "initial_positions": {
            "white": [(7, 2), (7, 5)],
            "black": [(0, 2), (0, 5)]
        },
        "valid_relative_moves": {
            "white": [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            "black": True
        },
        "valid_relative_captures": True,
        "displacement": 7,
        "value": 3
    },
    "queen": {
        "notation": "Q",
        "unicode": {
            "white": "♕",
            "black": "♛"
        },
        "initial_positions": {
            "white": [(7, 3)],
            "black": [(0, 3)]
        },
        "valid_relative_moves": {
            "white": [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            "black": True
        },
        "valid_relative_captures": True,
        "displacement": 7,
        "value": 9
    },
    "king": {
        "notation": "K",
        "unicode": {
            "white": "♔",
            "black": "♚"
        },
        "initial_positions": {
            "white": [(7, 4)],
            "black": [(0, 4)]
        },
        "valid_relative_moves": {
            "white": [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            "black": True
        },
        "valid_relative_captures": True,
        "displacement": 1,
        "value": 0
    }
}


@dataclass
class Piece:
    color: Literal["black", "white"]
    type: Literal["pawn", "rook", "knight", "bishop", "queen", "king"]
    notation: str = field(init=False)
    value: int = field(init=False)
    unicode: str = field(init=False)
    initial_positions: list[tuple[int, int]] = field(init=False)
    valid_relative_moves: list[tuple[int, int]] = field(init=False)
    valid_relative_captures: list[tuple[int, int]] = field(init=False)
    displacement: int = field(init=False)
    value: int = field(init=False)

    def __post_init__(self):
        valid_relative_moves = piece_dict[self.type]["valid_relative_moves"]
        valid_relative_captures = piece_dict[self.type]["valid_relative_captures"]

        # if valid_relative_captures is True, replace it with the valid_relative_moves and vice versa
        if valid_relative_moves is True:
            valid_relative_moves = valid_relative_captures
        if valid_relative_captures is True:
            valid_relative_captures = valid_relative_moves      

        # If there's a True in the valid_relative_moves or valid_relative_captures, 
        # replace it with the valid_relative_moves or valid_relative_captures for the piece's color
        if valid_relative_moves[self.color] is True:
            valid_relative_moves = valid_relative_moves["black" if self.color == "white" else "white"]
        if valid_relative_captures[self.color] is True:
            valid_relative_captures = valid_relative_captures["black" if self.color == "white" else "white"]

        logger.debug(f"Piece.__post_init__(): {self.color} {self.type}\n"
                     f"\tvalid_relative_moves: {valid_relative_moves}\n"
                     f"\tvalid_relative_captures: {valid_relative_captures}")

        # Set the notation, unicode, initial_positions, valid_relative_moves, valid_relative_captures, displacement, and value
        self.notation = piece_dict[self.type]["notation"]
        self.unicode = piece_dict[self.type]["unicode"][self.color]
        self.initial_positions = piece_dict[self.type]["initial_positions"][self.color]
        self.valid_relative_moves = valid_relative_moves
        self.valid_relative_captures = valid_relative_captures
        self.displacement = piece_dict[self.type]["displacement"]
        self.value = piece_dict[self.type]["value"]

        self._valid_moves = None

    @staticmethod
    def random_piece():
        """Returns a random piece"""
        return Piece(choice(["white", "black"]), choice(["pawn", "rook", "knight", "bishop", "queen", "king"]))

    def valid_moves(self, i, j):
        """Returns a list of all valid moves moves from an absolute position (i, j)
        that are generated by the piece's valid_relative_moves and valid_relative_captures.

        It considers displacement and the board's boundaries. (But not other pieces!)
        """
        if self._valid_moves is None:
            valid_moves = []
            logger.debug(f"Generated valid moves for {self.color} {self.type} at ({i}, {j})\n\tvalid_relative_moves: {self.valid_relative_moves}\n\tvalid_relative_captures: {self.valid_relative_captures}")

            moves = set(self.valid_relative_moves + self.valid_relative_captures)
            for relative_move in moves:
                for displacement in range(1, self.displacement + 1):
                    new_i, new_j = i + relative_move[0] * displacement, j + relative_move[1] * displacement
                    if 0 <= new_i < 8 and 0 <= new_j < 8:
                        valid_moves.append((new_i, new_j))
                    else:
                        break
            self._valid_moves = valid_moves

        return self._valid_moves
    
    def check_path(self, board, pos, new_pos):
        """Checks if the path from pos to new_pos is clear.
        Returns True if it is, False if it isn't.
        """
        relative_move = (new_pos[0] - pos[0], new_pos[1] - pos[1])
        if relative_move not in self.valid_relative_moves:
            return False

        for displacement in range(1, self.displacement + 1):
            new_i, new_j = pos[0] + relative_move[0] * displacement, pos[1] + relative_move[1] * displacement
            if new_i == new_pos[0] and new_j == new_pos[1]:
                return True
            if board[new_i][new_j] is not None:
                return False

    
    def __str__(self):
        return self.notation.upper() if self.color == "white" else self.notation.lower()
    
    def __hash__(self) -> int:
        return id(self)