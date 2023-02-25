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
    def __init__(self):
        self.reset()

    @staticmethod
    def initialize_board(no_pawns=False, 
                        no_left_pawns=False, 
                        no_right_pawns=False,
                        no_knights=False,
                        no_rooks=False,
                        no_bishops=False,
                        no_queens=False,
                        one_each=False,
                        interlace_pawns=False
    ):
        """Initializes the board with the starting positions of the pieces."""
        board = [[None for _ in range(8)] for _ in range(8)]

        for piece in piece_dict:
            if no_pawns and piece == "pawn":
                continue
            already_placed = []
            for color in piece_dict[piece]["initial_positions"]:
                for position in piece_dict[piece]["initial_positions"][color]:
                    if no_left_pawns and piece == "pawn":
                        if position[1] < 4:
                            continue
                    if no_right_pawns and piece == "pawn":
                        if position[1] > 3:
                            continue

                    if no_knights and piece == "knight":
                        continue
                    if no_rooks and piece == "rook":
                        continue
                    if no_bishops and piece == "bishop":
                        continue
                    if no_queens and piece == "queen":
                        continue

                    if one_each and piece != "pawn":
                        if position in already_placed:
                            continue
                        else:
                            already_placed.append(position)

                    if interlace_pawns and piece == "pawn":
                        if position[1] % 2 == 0:
                            continue

                    board[position[0]][position[1]] = Piece(color, piece)
                    
        return board
    
    def reset(self):
        """Resets the board to its initial state"""
        self._active_pieces = None
        self.board = Chessboard.initialize_board()

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
    
    # remove piece from active pieces
    def remove_piece(self, position):
        """Removes a piece from the board"""
        self.board[position[0]][position[1]] = None
        # find piece in active pieces
        for real_position, piece in self.active_pieces.items():
            if piece == position:
                del self.active_pieces[real_position]
                break 
       
    def valid_moves(self, position):
        """Returns a list of valid moves for a piece. """
        logger.debug(f"Getting valid moves for {self.board[position[0]][position[1]]} at {position}")

        valid_moves = []
        piece = self.board[position[0]][position[1]]
        if not piece:
            return []
        
        for move in piece.valid_relative_moves:
            for displacement in range(1, piece.displacement + 1):
                new_position = (position[0] + move[0] * displacement, position[1] + move[1] * displacement)
                if self.board_valid_move(position, new_position):
                    if piece.type in ["bishop", "rook", "queen"]:
                        if self.check_path(position, new_position):
                            valid_moves.append(new_position)
                    elif piece.type == "pawn":
                        if not self.board[new_position[0]][new_position[1]]:
                            valid_moves.append(new_position)
                        for capture in piece.valid_captures:
                            capture_position = (position[0] + capture[0], position[1] + capture[1])
                            if self.board_valid_move(position, capture_position):
                                p = self.get_piece_at(capture_position)
                                if p and not piece.compare_color(p):
                                    valid_moves.append(capture_position)
                            
                    else:
                        valid_moves.append(new_position)

        logger.debug(f"Valid moves for {piece} at {position}: {valid_moves}")
        return valid_moves
        
    def board_valid_move(self, position, new_position):
        """Checks if a move is valid between two locations on the board."""
        # check if new position is in bounds
        if new_position[0] < 0 or new_position[0] > 7 or new_position[1] < 0 or new_position[1] > 7:
            return False

        # check if move is to the same position
        if new_position == position:
            return False

        # check if move is to an occupied square by same team
        if self.board[new_position[0]][new_position[1]] and self.board[new_position[0]][new_position[1]].color == self.board[position[0]][position[1]].color:
            return False

        return True

    def check_path(self, position, new_position):
        """ Returns true if there are no pieces in a straight line between two positions. """
        # get the direction of the move
        direction = (new_position[0] - position[0], new_position[1] - position[1])

        # get the number of spaces between the two positions
        distance = max(abs(direction[0]), abs(direction[1]))

        # check if the path is clear
        seen_enemy = False
        for i in range(distance):
            # get the position of the next space in the path
            next_position = (position[0] + (i + 1) * direction[0] // distance, position[1] + (i + 1) * direction[1] // distance)
            # check if the space is occupied by a friendly piece
            if self.board[next_position[0]][next_position[1]] and self.board[next_position[0]][next_position[1]].color == self.board[position[0]][position[1]].color:
                return False
            # if it's an enemy piece, check if we've already seen one or set that we have
            elif self.board[next_position[0]][next_position[1]]:
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
        piece = self.board[position[0]][position[1]]
        if self.board[new_position[0]][new_position[1]]:
            self.remove_piece(new_position)
        self.board[new_position[0]][new_position[1]] = piece
        self.board[position[0]][position[1]] = None
        self._updated = True
    
    # define index access to board
    def __getitem__(self, key):
        piece = self.board[key[0]][key[1]]
        return piece