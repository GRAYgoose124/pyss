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
        "value": 0
    }
}


class Piece:           
    def __init__(self, 
                 color: Literal["black", "white"], 
                 piece_type: Literal["pawn", "rook", "knight", "bishop", "queen", "king"]
                ):
        self.color = color
        self.piece_type = piece_type
        self.notation = piece_dict[piece_type]["notation"]
        self.value = piece_dict[piece_type]["value"]
        self.unicode = piece_dict[self.piece_type]["unicode"][color]
        self.initial_positions = piece_dict[self.piece_type]["initial_positions"][color]
        
    @staticmethod
    def random_piece():
        """Returns a random piece"""
        return Piece(choice(["white", "black"]), choice(["pawn", "rook", "knight", "bishop", "queen", "king"]))

    def __str__(self):
        return self.notation[self.piece_type].upper() if self.color == "white" else self.notation[self.piece_type].lower()