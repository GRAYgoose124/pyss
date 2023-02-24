from dataclasses import dataclass, field
from random import choice
from typing import Literal


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

        # Set the notation, unicode, initial_positions, valid_relative_moves, valid_relative_captures, displacement, and value
        self.notation = piece_dict[self.type]["notation"]
        self.unicode = piece_dict[self.type]["unicode"][self.color]
        self.initial_positions = piece_dict[self.type]["initial_positions"][self.color]
        self.valid_relative_moves = valid_relative_moves
        self.valid_relative_captures = valid_relative_captures
        self.displacement = piece_dict[self.type]["displacement"]
        self.value = piece_dict[self.type]["value"]

    @staticmethod
    def random_piece():
        """Returns a random piece"""
        return Piece(choice(["white", "black"]), choice(["pawn", "rook", "knight", "bishop", "queen", "king"]))

    def __str__(self):
        return self.notation.upper() if self.color == "white" else self.notation.lower()
    
    def __hash__(self) -> int:
        return id(self)