import logging

from pyss.game.board.base import BaseBoard
from pyss.game.notation import generate_notation
from ..piece import piece_dict


logger = logging.getLogger(__name__)


class PlayableBoard(BaseBoard):
    def __init__(self, initialize=True):
        super().__init__(initialize=initialize)

        self.active_color = "white"

        self.move_history = []

        self.en_passant_available = False
        self._check = None
        self._checkmate = None

    def reset(self, **kwargs):
        super().reset(**kwargs)

        self.move_history = []

        self.en_passant_available = False
        self._check = None
        self._checkmate = None

    def get_valid_moves(self, position=None):
        """Returns a list of valid moves for a piece. """
        valid_moves = []
        piece = self[position]
        if not piece:
            return []

        if piece.type == "pawn":
            # TODO: check for promotion
            # check for en passant, self.en_passant_available is the position of the pawn that can be captured
            if self.en_passant_available:
                if self.en_passant_available[1] == position[1] and abs(self.en_passant_available[0] - position[0]) == 1:
                    valid_moves.append(self.en_passant_available)
        elif piece.type in ["king", "rook"]:
            # check for castling by checking if king and rook have moved
            if not piece.has_moved:
                # TODO: Should probably make a staticmethod to get initial positions for a given piece
                other_positions = piece_dict["rook" if piece.type ==
                                             "king" else "king"]["initial_positions"][piece.color]
                for other_pos in other_positions:
                    other_piece = self[other_pos]
                    if other_piece and not other_piece.has_moved:
                        # check if path is clear
                        if self.check_path(position, other_pos, castling=True):
                            valid_moves.append(other_pos)

        for move in piece.valid_relative_moves:
            for displacement in range(1, piece.displacement + 1):
                new_position = (
                    position[0] + move[0] * displacement,
                    position[1] + move[1] * displacement)
                if self.board_safe(position, new_position):
                    if piece.type in ["bishop", "rook", "queen"]:
                        if self.check_path(position, new_position):
                            valid_moves.append(new_position)
                    elif piece.type == "pawn":
                        if not self[new_position]:
                            valid_moves.append(new_position)
                        for capture in piece.valid_captures:
                            capture_position = (
                                position[0] + capture[0], position[1] + capture[1])
                            if self.board_safe(position, capture_position):
                                p = self[capture_position]
                                if p and not piece.compare_color(p):
                                    valid_moves.append(capture_position)

                        # if initial position, check two squares
                        if position in piece.initial_positions:
                            new_position = (
                                position[0] + move[0] * 2,
                                position[1] + move[1] * 2)
                            if self.check_path(position, new_position):
                                if not self[new_position]:
                                    valid_moves.append(new_position)
                    else:
                        valid_moves.append(new_position)

        # logger.debug(f"Valid moves for {piece} at {position}: {valid_moves}")
        return valid_moves

    def __find_check(self, position):
        """Returns true if the king is threatened by position."""
        # get the piece at the position
        piece = self[position]
        # see if the piece can see a king
        if piece:
            # TODO: use _selected_valid_moves instead of valid_moves
            for move in self.get_valid_moves(position):
                next_piece = self[move]
                if next_piece and next_piece.type == "king" and not next_piece.compare_color(piece):
                    return move

        return False

    def __find_checkmate(self, position):
        # if king has no valid moves, it's checkmate
        return False

    def move(self, position, new_position, update=False):
        """ Semi-unsafely moves a piece destroying any piece that is in the destination.
            This expects that the move is valid under chess rules. 
        """
        en_passanted = False
        capture = False
        castled = False

        piece = self[position]
        other = self[new_position]

        # lets quit before we do anything if there's no piece to move
        if not piece:
            return

        # check if the move is a castle, this presumes that it's a valid castle. (semi-unsafe)
        if piece.type in ["king", "rook"] and other and other.type in ["king", "rook"] and\
                other.type != piece.type and other.color == piece.color:
            del self[new_position]
            del self[position]

            # castle the king and rook
            # TODO: should castle be stored in the pieces?
            # right rook moving
            if position[0] == 7:
                king, rook = (5, 6)
                castled = "kingside"
            # left rook moving
            elif position[0] == 0:
                king, rook = (3, 2)
                castled = "queenside"
            # king
            else:
                # moving right
                if position[0] < new_position[0]:
                    king, rook = (6, 5)
                    castled = "kingside"
                # moving left
                else:
                    king, rook = (2, 3)
                    castled = "queenside"

            other.has_moved = True
            piece.has_moved = True
            self[king if other.type == "king" else rook, position[1]] = other
            self[king if piece.type == "king" else rook, position[1]] = piece
        else:
            # if king, you cannot take, only check and checkmate
            if other and other.type == "king":
                return

            # reset en passant state if not pawn moving.
            # This is partially destructive and part of why this is a semi-unsafe move.
            if piece.type != "pawn" and self.en_passant_available:
                self.en_passant_available = False

            if piece.type == "pawn":
                # TODO: check for promotions
                # Jump + En Passant
                if abs(new_position[1] - position[1]) == 2 and position in piece.initial_positions:
                    self.en_passant_available = new_position
                else:
                    # check if pawn is capturing en passant, en_passant_available is the position of the pawn that can be captured
                    vector = (new_position[0] - position[0],
                              new_position[1] - position[1])
                    logger.debug("Vector: ", vector, "Valid Captures: ", piece.valid_captures,
                                 "En Passant Available: ", self.en_passant_available)
                    if self.en_passant_available and new_position == self.en_passant_available and vector not in piece.valid_captures:
                        del self[self.en_passant_available]
                        en_passanted = True
                        # new position is actually behind the captured pawn
                        new_position = (new_position[0], self.en_passant_available[1] + 1 if piece.color ==
                                        "white" else self.en_passant_available[1] - 1)
                    self.en_passant_available = False

            # move the piece
            del self[position]
            self[new_position] = piece
            piece.has_moved = True

        # check if the move is a capture
        if other:
            capture = True

        # check if king is threatened
        # This si not working, presumably because valid moves isn't correct.
        check_position = self.__find_check(new_position)
        if check_position:
            self._check = check_position
            if self.__find_checkmate(new_position):
                self._checkmate = check_position
        else:
            self._check = None
            self._checkmate = None

        # TODO: to append check/checkmate it must be checked here...
        self.move_history.append(generate_notation(
            piece.type, piece.notation, position, new_position, capture=capture,
            en_passant=en_passanted, check=self._check, checkmate=self._checkmate, castle=castled)
        )
