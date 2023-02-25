import logging
import yaml
import os

from dataclasses import dataclass, field
from random import choice
from typing import Literal


logger = logging.getLogger(__name__)


try:
    # get dir piece.py is in
    root = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(root, "data/piece_dict.yaml"), "r") as f:
        piece_dict = yaml.unsafe_load(f)
except Exception as e:
    print(e)
    print("Using default piece_dict!")


@dataclass
class Piece:
    COLORS = Literal["white", "black"]
    TYPES = Literal["pawn", "rook", "knight", "bishop", "queen", "king"]

    POSITION = tuple[int, int]

    color: COLORS
    type: TYPES

    notation: str = field(init=False)
    value: int = field(init=False)
    unicode: str = field(init=False)
    initial_positions: list[POSITION] = field(init=False)
    displacement: int = field(init=False)
    value: int = field(init=False)

    # need to be transformed into real moves by multiply with displacement
    valid_relative_moves: list[POSITION] = field(init=False)

    def __post_init__(self):
        valid_relative_moves = piece_dict[self.type]["valid_relative_moves"]
        if self.type == "pawn":
            valid_relative_moves = valid_relative_moves[self.color]
            # valid_captures is pawn only! TODO?
            valid_captures = piece_dict[self.type]["valid_captures"][self.color]
            self.valid_captures = valid_captures

        logger.debug(f"Piece.__post_init__(): {self.color} {self.type}\n"
                     f"\tvalid_relative_moves: {valid_relative_moves}\n")

        # Set the notation, unicode, initial_positions, valid_relative_moves,
        # valid_relative_captures, displacement, and value
        self.notation = piece_dict[self.type]["notation"]
        self.unicode = piece_dict[self.type]["unicode"][self.color]
        self.initial_positions = piece_dict[self.type]["initial_positions"][self.color]
        self.valid_relative_moves = valid_relative_moves
        self.displacement = piece_dict[self.type]["displacement"]
        self.value = piece_dict[self.type]["value"]

        self._valid_moves = None

    @staticmethod
    def random_piece():
        """Returns a random piece"""
        return Piece(choice(Piece.COLORS.__args__),
                     choice(Piece.TYPES.__args__))

    def compare_color(self, other):
        """Returns True if the colors of self and other are the same"""
        return self.color == other.color
    
    def compare(self, other):
        """Return a dict of the different fields."""
        diff = {}
        for field in ["color", "type"]:
            if getattr(self, field) != getattr(other, field):
                diff[field] = getattr(other, field)
        return diff

    def __str__(self):
        return self.notation.upper() if self.color == "white" else self.notation.lower()

    def __hash__(self) -> int:
        return id(self)
