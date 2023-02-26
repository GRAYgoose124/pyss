from copy import deepcopy
import logging

from functools import lru_cache
from .piece import piece_dict, Piece


logger = logging.getLogger(__name__)


class Chessboard:
    """Represents a chessboard

        - 8x8 grid of alternating black and white squares
        - 16 pieces per player
        - 2 players
    """

    def __init__(self, initialize=True):
        self.reset(initialize=initialize)

    @staticmethod
    def initialize_board(no_pawns=False,
                         no_left_pawns=False,
                         no_right_pawns=False,
                         no_knights=False,
                         no_rooks=False,
                         no_bishops=False,
                         no_queens=False,
                         one_each=False,
                         interlace_pawns=False,
                         no_initial_pieces=False,
                         ):
        """Initializes the board with the starting positions of the pieces."""
        board = [[None for _ in range(8)] for _ in range(8)]

        if not no_initial_pieces:
            for ty in piece_dict:
                if no_pawns and ty == "pawn":
                    continue
                already_placed = []
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

                        if one_each and ty != "pawn":
                            if position in already_placed:
                                continue
                            else:
                                already_placed.append(position)

                        if interlace_pawns and ty == "pawn":
                            if position[1] % 2 == 0:
                                continue

                        board[position[0]][position[1]] = Piece(color, ty)

        return board

    def reset(self, initialize=True):
        """Resets the board to its initial state"""
        self._active_pieces = None
        self._last_move = None
        self.en_passant_available = False
        self.board = Chessboard.initialize_board(
            no_initial_pieces=not initialize)

    @property
    def active_pieces(self):
        """Returns a list of all the pieces on the board"""
        if self._active_pieces:
            return self._active_pieces

        pieces = {}
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece:
                    pieces[piece] = (i, j)

        return pieces

    @property
    def last_move(self):
        """Returns the last move made on the board"""
        return self._last_move

    # remove piece from active pieces
    def remove_piece(self, position):
        """Removes a piece from the board"""
        self.board[position[0]][position[1]] = None
        # find piece in active pieces
        for real_position, piece in self.active_pieces.items():
            if piece == position:
                del self.active_pieces[real_position]
                break

    def valid_moves_to_depth(self, position, depth=3, all_valid_moves=None):
        """Returns a list of valid moves for a piece to a given depth. (max=3) """
        if all_valid_moves is None:
            all_valid_moves = []

        original_piece = self.get_piece_at(position)
        if not original_piece or depth < 0:
            return all_valid_moves

        # check valid moves for piece
        valid_moves = self.valid_moves(position)
        all_valid_moves.append((depth, valid_moves))
        for move in valid_moves:
            # simulate move
            move_piece = self.get_piece_at(move)
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
        piece = self.get_piece_at(position)
        if not piece:
            return []

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
                        if not self.get_piece_at(new_position):
                            valid_moves.append(new_position)
                        for capture in piece.valid_captures:
                            capture_position = (
                                position[0] + capture[0], position[1] + capture[1])
                            if self.board_safe(position, capture_position):
                                p = self.get_piece_at(capture_position)
                                if p and not piece.compare_color(p):
                                    valid_moves.append(capture_position)

                        # if initial position, check two squares
                        if position in piece.initial_positions:
                            new_position = (
                                position[0] + move[0] * 2,
                                position[1] + move[1] * 2)
                            if self.board_safe(position, new_position):
                                if not self.get_piece_at(new_position):
                                    valid_moves.append(new_position)

                        # check for en passant, self.en_passant_available is the position of the pawn that can be captured
                        if self.en_passant_available:
                            if self.en_passant_available[0] == position[0] and abs(self.en_passant_available[1] - position[1]) == 1:
                                valid_moves.append(self.en_passant_available)
                            
                        # TODO: check for promotion
                    else:
                        valid_moves.append(new_position)

        logger.debug(f"Valid moves for {piece} at {position}: {valid_moves}")
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
        dest_piece = self.get_piece_at(new_position)
        moving_piece = self.get_piece_at(position)
        if dest_piece and moving_piece and dest_piece.color == moving_piece.color:
            return False

        return True

    def check_path(self, position, new_position):
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
        for i in range(distance):
            # get the position of the next space in the path
            next_position = (position[0] +
                             (i + 1) * direction[0] // distance,
                             position[1] +
                             (i + 1) * direction[1] // distance)

            # check if the space is occupied by a friendly piece
            next_piece = self.get_piece_at(next_position)
            moving_piece = self.get_piece_at(position)
            if next_piece and moving_piece and next_piece.compare_color(
                    moving_piece):
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

    def get_piece_at(self, position):
        """Returns the piece at a given position"""
        return self.board[position[0]][position[1]]

    def move(self, position, new_position):
        """ Unsafely moves a piece destroying any piece that is in the destionatoin. """
        piece = self.get_piece_at(position)
        if not piece:
            return

        if piece.type != "pawn" and self.en_passant_available:
            self.en_passant_available = False

        if piece.type == "pawn":                
            # check if pawn is moving two spaces from initial position
            if abs(new_position[0] - position[0]) == 2 and position in piece.initial_positions:
                self.en_passant_available = new_position
            else:
                # check if pawn is capturing en passant, en_passant_available is the position of the pawn that can be captured
                vector = (new_position[0] - position[0], new_position[1] - position[1])
                if self.en_passant_available and new_position == self.en_passant_available and vector not in piece.valid_captures:
                    self.remove_piece(self.en_passant_available)
                    # new position is actually behind the captured pawn
                    new_position = (self.en_passant_available[0] - 1 if piece.color == "white" else self.en_passant_available[0] + 1, new_position[1])
                self.en_passant_available = False
        else:
            if self.board[new_position[0]][new_position[1]]:
                self.remove_piece(new_position)

        self.board[new_position[0]][new_position[1]] = piece
        self.board[position[0]][position[1]] = None
        self._updated = True

    # define index access to board
    def __getitem__(self, key):
        piece = self.board[key[0]][key[1]]
        return piece
