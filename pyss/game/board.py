from copy import deepcopy
import logging

from functools import lru_cache

from pyss.game.notation import generate_notation
from .piece import piece_dict, Piece


logger = logging.getLogger(__name__)


class Chessboard:
    """Represents a chessboard

        - 8x8 grid of alternating black and white squares
        - 16 pieces per player
        - 2 players
    """

    def __init__(self, initialize=True):
        self.en_passant_available = False
        self.board = None
        self.move_history = []

        self._active_pieces = None
        self._by_color = None

        self._check = None
        self._checkmate = None

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
        self.move_history = []
        self.en_passant_available = False

        self._check = None
        self._checkmate = None
        
        self.board = Chessboard.initialize(**kwargs)
        self.__init_active_pieces()

    def __init_active_pieces(self):
        """Updates the active pieces on the board"""

        pieces = {}
        by_color = {'white': [], 'black': []}
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece:
                    pieces[piece] = (i, j)
                    by_color[piece.color].append(piece)

        self._by_color = by_color
        self._active_pieces = pieces

    def valid_moves_to_depth(self, position, depth=3, all_valid_moves=None):
        """Returns a list of valid moves for a piece to a given depth. (max=3) """
        if all_valid_moves is None:
            all_valid_moves = []

        original_piece = self[position]
        if not original_piece or depth < 0:
            return all_valid_moves

        # check valid moves for piece
        valid_moves = self.valid_moves(position)
        all_valid_moves.append((depth, valid_moves))
        for move in valid_moves:
            # simulate move - we don't use getters/setters here because we don't want to update the board
            move_piece = self[move]
            self.board[move[0]][move[1]] = original_piece

            # check valid moves for piece
            self.board[position[0]][position[1]] = None
            self.valid_moves_to_depth(
                move, depth=depth - 1, all_valid_moves=all_valid_moves)

            # undo move
            self.board[move[0]][move[1]] = move_piece
            self.board[position[0]][position[1]] = original_piece

        return all_valid_moves

    def valid_moves(self, position=None):
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
                other_positions = Piece(
                    piece.color, "rook" if piece.type == "king" else "king").initial_positions
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

    def check_path(self, position, new_position, castling=False):
        """ Returns true if there are no pieces in a straight line between two positions. """
        # get the direction of the move
        direction = (
            new_position[0] -
            position[0],
            new_position[1] -
            position[1])

        # get the number of spaces between the two positions
        distance = max(abs(direction[0]), abs(direction[1]))
        # TODO: Hack so that castling doesn't ignore rooks/kings

        # check if the path is clear
        seen_enemy = False
        for i in range(distance):
            # get the position of the next space in the path
            next_position = (position[0] +
                             (i + 1) * direction[0] // distance,
                             position[1] +
                             (i + 1) * direction[1] // distance)

            # check if the space is occupied by a friendly piece
            next_piece = self[*next_position]
            moving_piece = self[*position]
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
    
    def __find_check(self, position):
        """Returns true if the king is threatened by position."""
        # get the piece at the position
        piece = self[position]
        # see if the piece can see a king
        if piece:
            # TODO: use _selected_valid_moves instead of valid_moves
            for move in self.valid_moves(position):
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

        piece = self[*position]
        other = self[*new_position]

        # lets quit before we do anything if there's no piece to move
        if not piece:
            return

        # check if the move is a castle, this presumes that it's a valid castle. (semi-unsafe)
        if piece.type in ["king", "rook"]:
            if other and other.type in ["king", "rook"] and other.type != piece.type:
                del self[*new_position]
                del self[*position]

                # castle the king and rook
                # the rooks can be on either side of the king and 2 or 3 spaces away
                # the right rook will end up on file 5 and the left on file 3
                # the king will move +2 or -2 spaces
                # left rook
                if position[1] == 7:
                    other_position = (position[0], 5)
                    piece_position = (position[0], 4)
                # right rook
                elif position[1] == 0:
                    other_position = (position[0], 1)
                    piece_position = (position[0], 2)
                # king
                else:
                    # moving right
                    if position[1] < new_position[1]:
                        other_position = (position[0], 4)
                        piece_position = (position[0], 5)
                    # moving left
                    else:
                        other_position = (position[0], 2)
                        piece_position = (position[0], 1)

                self[other_position] = other
                self[piece_position] = piece

                return

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
                logger.debug("Vector: ", vector, "Valid Captures: ", piece.valid_captures, "En Passant Available: ", self.en_passant_available)
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
            en_passant=en_passanted, check=self._check, checkmate=self._checkmate)
        )
        
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
        for real_position, piece in self._active_pieces.items():
            if piece == key:
                del self._active_pieces[real_position]
                self._by_color[self[piece].color].remove(real_position)
                break

        self.board[key[0]][key[1]] = None

    def __setitem__(self, key, value):
        """Adds a piece to the board"""
        # if already a piece there, remove it
        if self[key]:
            del self[key]

        self.board[key[0]][key[1]] = value
        self._active_pieces[value] = key
        self._by_color[value.color].append(value)
