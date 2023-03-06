from copy import deepcopy
import logging

from functools import lru_cache

from pyss.game.notation import generate_notation
from pyss.game.piece import piece_dict, Piece


logger = logging.getLogger(__name__)


class BaseBoard:
    """Represents a chessboard

        - 8x8 grid of alternating black and white squares
        - 16 pieces per player
        - 2 players
    """

    def __init__(self, initialize=True):
        self.board = None

        self._active_pieces = None
        self._by_color = None

        if initialize:
            self.reset()

    @staticmethod
    def initialize(no_pawns=False,
                   no_left_pawns=False,
                   no_right_pawns=False,
                   no_knights=False,
                   no_rooks=False,
                   no_bishops=False,
                   no_queens=False,
                   no_second_special=False,
                   interlace_pawns=False,
                   no_initial_pieces=False,
                   ):
        """Initializes the board with the starting positions of the pieces."""
        board = [[None for _ in range(8)] for _ in range(8)]

        if not no_initial_pieces:
            already_placed = {'white': [], 'black': []}

            for ty in piece_dict:
                if no_pawns and ty == "pawn":
                    continue
                for color in piece_dict[ty]["initial_positions"]:
                    for position in piece_dict[ty]["initial_positions"][color]:
                        if no_left_pawns and ty == "pawn":
                            if position[1] < 4:
                                continue
                        if no_right_pawns and ty == "pawn":
                            if position[1] > 3:
                                continue

                        if no_knights and ty == "knight":
                            continue
                        if no_rooks and ty == "rook":
                            continue
                        if no_bishops and ty == "bishop":
                            continue
                        if no_queens and ty == "queen":
                            continue

                        if no_second_special and ty != "pawn":
                            if ty in already_placed[color]:
                                continue
                            else:
                                already_placed[color].append(ty)

                        if interlace_pawns and ty == "pawn":
                            if position[1] % 2 == 0:
                                continue

                        board[position[0]][position[1]] = Piece(color, ty)

        return board

    def reset(self, **kwargs):
        """Resets the board to its initial state"""
        self.board = BaseBoard.initialize(**kwargs)
        self.__init_active_pieces()

    @property
    def active_pieces(self):
        """Returns a dictionary of the active pieces on the board"""
        return self._active_pieces

    @property
    def by_color(self):
        """Returns a dictionary of the active pieces on the board"""
        return self._by_color

    def __init_active_pieces(self):
        """Updates the active pieces on the board"""

        pieces = {}
        by_color = {'white': {}, 'black': {}}
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece:
                    pieces[piece] = (i, j)
                    by_color[piece.color][piece] = (i, j)

        self._by_color = by_color
        self._active_pieces = pieces

    def board_safe(self, position, new_position):
        """Checks if a move is valid between two locations on the board."""
        # check if new position is in bounds
        if new_position[0] < 0 or new_position[0] > 7 or new_position[1] < 0 or new_position[1] > 7:
            return False

        # check if move is to the same position
        if new_position == position:
            return False

        # check if move is to an occupied square by same team
        dest_piece = self[new_position]
        moving_piece = self[position]
        if dest_piece and moving_piece and dest_piece.color == moving_piece.color:
            return False

        return True

    def check_path(self, position, new_position, castling=False, blockers=None):
        """ Returns true if there are no pieces in a straight line between two positions. """
        # get the direction of the move
        direction = (
            new_position[0] -
            position[0],
            new_position[1] -
            position[1])

        # get the number of spaces between the two positions
        distance = max(abs(direction[0]), abs(direction[1]))

        # check if the path is clear
        seen_enemy = False
        moving_piece = self[position]
        for i in range(distance):
            # get the position of the next space in the path
            next_position = (position[0] +
                             (i + 1) * direction[0] // distance,
                             position[1] +
                             (i + 1) * direction[1] // distance)
            
            
            if blockers is not None:
                logger.debug(f"Checking blockers: {next_position} in {blockers}")
                if next_position in blockers:
                    return False
            
            # check if the space is occupied by a friendly piece
            next_piece = self[next_position]
            if next_piece and moving_piece and next_piece.compare_color(moving_piece) and\
                    next_piece.type not in ["king", "rook"] and not castling:
                return False
            # if it's an enemy piece, check if we've already seen one or set
            # that we have
            elif next_piece:
                if seen_enemy:
                    return False
                seen_enemy = True
            elif seen_enemy:
                return False

        return True

    # define index access to board
    def __getitem__(self, key):
        """Returns the piece at a position on the board"""
        try:
            piece = self.board[key[0]][key[1]]
            return piece
        except IndexError:
            pass

    def __delitem__(self, key):
        """Removes a piece from the board"""
        # find piece in active pieces
        for item in self._active_pieces.items():
            if item[1] == key:
                del self._active_pieces[item[0]]
                bc = self._by_color[item[0].color]

                del bc[item[0]]
                break

        self.board[key[0]][key[1]] = None

    def __setitem__(self, key, value):
        """Adds a piece to the board"""
        # if already a piece there, remove it
        if self[key]:
            del self[key]

        self.board[key[0]][key[1]] = value
        self._active_pieces[value] = key
        self._by_color[value.color][value] = key
